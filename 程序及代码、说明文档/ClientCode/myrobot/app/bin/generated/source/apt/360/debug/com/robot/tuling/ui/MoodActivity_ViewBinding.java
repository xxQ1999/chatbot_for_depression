// Generated code from Butter Knife. Do not modify!
package com.robot.tuling.ui;

import android.support.annotation.CallSuper;
import android.support.annotation.UiThread;
import android.support.v7.widget.Toolbar;
import android.view.View;
import butterknife.Unbinder;
import butterknife.internal.Utils;
import com.robot.tuling.R;
import java.lang.IllegalStateException;
import java.lang.Override;

public class MoodActivity_ViewBinding implements Unbinder {
  private MoodActivity target;

  @UiThread
  public MoodActivity_ViewBinding(MoodActivity target) {
    this(target, target.getWindow().getDecorView());
  }

  @UiThread
  public MoodActivity_ViewBinding(MoodActivity target, View source) {
    this.target = target;

    target.toolbar = Utils.findRequiredViewAsType(source, R.id.toolbar, "field 'toolbar'", Toolbar.class);
  }

  @Override
  @CallSuper
  public void unbind() {
    MoodActivity target = this.target;
    if (target == null) throw new IllegalStateException("Bindings already cleared.");
    this.target = null;

    target.toolbar = null;
  }
}
