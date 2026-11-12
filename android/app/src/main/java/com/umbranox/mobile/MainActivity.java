package com.umbranox.mobile;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.chaquo.python.PyException;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final String SERVER_URL = "http://127.0.0.1:5000";
    private final ExecutorService startupExecutor = Executors.newSingleThreadExecutor();
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        showStartupMessage("Preparando o jogo...");
        startupExecutor.execute(() -> {
            try {
                copyAssets("", new File(getFilesDir(), "frontend"));
                if (!Python.isStarted()) {
                    Python.start(new AndroidPlatform(this));
                }
                Python.getInstance()
                        .getModule("embedded_server")
                        .callAttr("start", getFilesDir().getAbsolutePath(),
                                new File(getFilesDir(), "frontend").getAbsolutePath());
                runOnUiThread(this::openGame);
            } catch (IOException | PyException e) {
                runOnUiThread(() -> showStartupError(e));
            }
        });
    }

    private void copyAssets(String path, File destination) throws IOException {
        String[] entries = getAssets().list(path);
        if (entries == null || entries.length == 0) {
            File parent = destination.getParentFile();
            if (parent != null && !parent.exists() && !parent.mkdirs()) {
                throw new IOException("Não foi possível criar a pasta de arquivos do jogo.");
            }
            try (InputStream input = getAssets().open(path);
                 FileOutputStream output = new FileOutputStream(destination)) {
                byte[] buffer = new byte[8192];
                int count;
                while ((count = input.read(buffer)) != -1) {
                    output.write(buffer, 0, count);
                }
            }
            return;
        }

        if (!destination.exists() && !destination.mkdirs()) {
            throw new IOException("Não foi possível criar a pasta de arquivos do jogo.");
        }
        for (String entry : entries) {
            String childPath = path.isEmpty() ? entry : path + "/" + entry;
            copyAssets(childPath, new File(destination, entry));
        }
    }

    private void showStartupMessage(String message) {
        TextView status = new TextView(this);
        status.setText(message);
        status.setTextSize(18);
        int padding = (int) (24 * getResources().getDisplayMetrics().density);
        status.setPadding(padding, padding, padding, padding);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.addView(status);
        setContentView(layout);
    }

    private void showStartupError(Exception error) {
        new AlertDialog.Builder(this)
                .setTitle("Não foi possível iniciar o jogo")
                .setMessage(error.getMessage() == null
                        ? "O servidor local encontrou um erro."
                        : error.getMessage())
                .setPositiveButton("Tentar novamente", (dialog, which) -> recreate())
                .setNegativeButton("Fechar", (dialog, which) -> finish())
                .show();
    }

    private void openGame() {
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view,
                                                               WebResourceRequest request) {
                String origin = request.getUrl().getScheme() + "://"
                        + request.getUrl().getAuthority();
                if (!SERVER_URL.equals(origin)) {
                    return new WebResourceResponse(
                            "text/plain", "UTF-8", new ByteArrayInputStream(new byte[0]));
                }
                return super.shouldInterceptRequest(view, request);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String origin = request.getUrl().getScheme() + "://"
                        + request.getUrl().getAuthority();
                return !SERVER_URL.equals(origin);
            }
        });
        setContentView(webView);
        webView.loadUrl(SERVER_URL);
    }

    @Override
    protected void onDestroy() {
        startupExecutor.shutdownNow();
        if (webView != null) {
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
