// Generated code from Butter Knife. Do not modify!
package com.robot.tuling.ui;

import android.support.annotation.CallSuper;
import android.support.annotation.UiThread;
import android.support.v7.widget.Toolbar;
import android.view.View;
import butterknife.Unbinder;
import butterknife.internal.Utils;
import com.robot.tuling.R;
import com.robot.tuling.widget.refreshswipemenulistview.XListView;
import java.lang.IllegalStateException;
import java.lang.Override;

public class NewsActivity_ViewBinding implements Unbinder {
  private NewsActivity target;

  @UiThread
  public NewsActivity_ViewBinding(NewsActivity target) {
    this(target, target.getWindow().getDecorView());
  }

  @UiThread
  public NewsActivity_ViewBinding(NewsActivity target, View source) {
    this.target = target;

    target.toolbar = Utils.findRequiredViewAsType(source, R.id.toolbar, "field 'toolbar'", Toolbar.class);
    target.xlvListView = Utils.findRequiredViewAsType(source, R.id.xlv_listView, "field 'xlvListView'", XListView.class);
  }

  @Override
  @CallSuper
  public void unbind() {
    NewsActivity target = this.target;
    if (target == null) throw new IllegalStateException("Bindings already cleared.");
    this.target = null;

    target.toolbar = null;
    target.xlvListView = null;
  }
}
