// Generated code from Butter Knife. Do not modify!
package com.robot.tuling.adapter;

import android.support.annotation.CallSuper;
import android.support.annotation.UiThread;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import butterknife.Unbinder;
import butterknife.internal.Utils;
import com.robot.tuling.R;
import java.lang.IllegalStateException;
import java.lang.Override;

public class NewsAdapter$ViewHolder_ViewBinding implements Unbinder {
  private NewsAdapter.ViewHolder target;

  @UiThread
  public NewsAdapter$ViewHolder_ViewBinding(NewsAdapter.ViewHolder target, View source) {
    this.target = target;

    target.ivNewsIcon = Utils.findRequiredViewAsType(source, R.id.iv_news_icon, "field 'ivNewsIcon'", ImageView.class);
    target.tvNewsTitle = Utils.findRequiredViewAsType(source, R.id.tv_news_title, "field 'tvNewsTitle'", TextView.class);
    target.tvNewsContent = Utils.findRequiredViewAsType(source, R.id.tv_news_content, "field 'tvNewsContent'", TextView.class);
  }

  @Override
  @CallSuper
  public void unbind() {
    NewsAdapter.ViewHolder target = this.target;
    if (target == null) throw new IllegalStateException("Bindings already cleared.");
    this.target = null;

    target.ivNewsIcon = null;
    target.tvNewsTitle = null;
    target.tvNewsContent = null;
  }
}
