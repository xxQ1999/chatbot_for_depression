// Generated code from Butter Knife. Do not modify!
package com.robot.tuling.ui;

import android.support.annotation.CallSuper;
import android.support.annotation.UiThread;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.webkit.WebView;
import butterknife.Unbinder;
import butterknife.internal.Utils;
import com.robot.tuling.R;
import java.lang.IllegalStateException;
import java.lang.Override;

public class DetailActivity_ViewBinding implements Unbinder {
  private DetailActivity target;

  @UiThread
  public DetailActivity_ViewBinding(DetailActivity target) {
    this(target, target.getWindow().getDecorView());
  }

  @UiThread
  public DetailActivity_ViewBinding(DetailActivity target, View source) {
    this.target = target;

    target.toolbar = Utils.findRequiredViewAsType(source, R.id.toolbar, "field 'toolbar'", Toolbar.class);
    target.webView = Utils.findRequiredViewAsType(source, R.id.webView, "field 'webView'", WebView.class);
  }

  @Override
  @CallSuper
  public void unbind() {
    DetailActivity target = this.target;
    if (target == null) throw new IllegalStateException("Bindings already cleared.");
    this.target = null;

    target.toolbar = null;
    target.webView = null;
  }
}
