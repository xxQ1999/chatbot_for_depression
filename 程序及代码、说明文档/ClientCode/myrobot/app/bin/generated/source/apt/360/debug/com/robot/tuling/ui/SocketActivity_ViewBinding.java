// Generated code from Butter Knife. Do not modify!
package com.robot.tuling.ui;

import android.support.annotation.CallSuper;
import android.support.annotation.UiThread;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.TextView;
import butterknife.Unbinder;
import butterknife.internal.Utils;
import com.ant.liao.GifView;
import com.robot.tuling.R;
import java.lang.IllegalStateException;
import java.lang.Override;

public class SocketActivity_ViewBinding implements Unbinder {
  private SocketActivity target;

  @UiThread
  public SocketActivity_ViewBinding(SocketActivity target) {
    this(target, target.getWindow().getDecorView());
  }

  @UiThread
  public SocketActivity_ViewBinding(SocketActivity target, View source) {
    this.target = target;

    target.toolbar = Utils.findRequiredViewAsType(source, R.id.toolbar, "field 'toolbar'", Toolbar.class);
    target.gvAbout = Utils.findRequiredViewAsType(source, R.id.gv_about, "field 'gvAbout'", GifView.class);
    target.lrTitle = Utils.findRequiredViewAsType(source, R.id.lr_title, "field 'lrTitle'", TextView.class);
    target.tvVersionRight = Utils.findRequiredViewAsType(source, R.id.tv_version_right, "field 'tvVersionRight'", LinearLayout.class);
  }

  @Override
  @CallSuper
  public void unbind() {
    SocketActivity target = this.target;
    if (target == null) throw new IllegalStateException("Bindings already cleared.");
    this.target = null;

    target.toolbar = null;
    target.gvAbout = null;
    target.lrTitle = null;
    target.tvVersionRight = null;
  }
}
