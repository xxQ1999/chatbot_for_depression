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

public class HelpActivity_ViewBinding implements Unbinder {
  private HelpActivity target;

  @UiThread
  public HelpActivity_ViewBinding(HelpActivity target) {
    this(target, target.getWindow().getDecorView());
  }

  @UiThread
  public HelpActivity_ViewBinding(HelpActivity target, View source) {
    this.target = target;

    target.toolbar = Utils.findRequiredViewAsType(source, R.id.toolbar, "field 'toolbar'", Toolbar.class);
    target.lvMessage2 = Utils.findRequiredViewAsType(source, R.id.lv_message2, "field 'lvMessage2'", ListView.class);
    target.ivSendMsg2 = Utils.findRequiredViewAsType(source, R.id.iv_send_msg2, "field 'ivSendMsg2'", ImageView.class);
    target.etMsg2 = Utils.findRequiredViewAsType(source, R.id.et_msg2, "field 'etMsg2'", EditText.class);
    target.rlMsg2 = Utils.findRequiredViewAsType(source, R.id.rl_msg2, "field 'rlMsg2'", RelativeLayout.class);
  }

  @Override
  @CallSuper
  public void unbind() {
    HelpActivity target = this.target;
    if (target == null) throw new IllegalStateException("Bindings already cleared.");
    this.target = null;

    target.toolbar = null;
    target.lvMessage2 = null;
    target.ivSendMsg2 = null;
    target.etMsg2 = null;
    target.rlMsg2 = null;
  }
}
