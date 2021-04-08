// Generated code from Butter Knife. Do not modify!
package com.robot.tuling.ui;

import android.support.annotation.CallSuper;
import android.support.annotation.UiThread;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.RelativeLayout;
import butterknife.Unbinder;
import butterknife.internal.Utils;
import com.robot.tuling.R;
import java.lang.IllegalStateException;
import java.lang.Override;

public class MainActivity_ViewBinding implements Unbinder {
  private MainActivity target;

  @UiThread
  public MainActivity_ViewBinding(MainActivity target) {
    this(target, target.getWindow().getDecorView());
  }

  @UiThread
  public MainActivity_ViewBinding(MainActivity target, View source) {
    this.target = target;

    target.toolbar = Utils.findRequiredViewAsType(source, R.id.toolbar, "field 'toolbar'", Toolbar.class);
    target.lvMessage = Utils.findRequiredViewAsType(source, R.id.lv_message, "field 'lvMessage'", ListView.class);
    target.ivSendMsg = Utils.findRequiredViewAsType(source, R.id.iv_send_msg, "field 'ivSendMsg'", ImageView.class);
    target.etMsg = Utils.findRequiredViewAsType(source, R.id.et_msg, "field 'etMsg'", EditText.class);
    target.rlMsg = Utils.findRequiredViewAsType(source, R.id.rl_msg, "field 'rlMsg'", RelativeLayout.class);
  }

  @Override
  @CallSuper
  public void unbind() {
    MainActivity target = this.target;
    if (target == null) throw new IllegalStateException("Bindings already cleared.");
    this.target = null;

    target.toolbar = null;
    target.lvMessage = null;
    target.ivSendMsg = null;
    target.etMsg = null;
    target.rlMsg = null;
  }
}
