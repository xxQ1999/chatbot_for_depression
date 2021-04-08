package com.robot.tuling.control;

import android.content.Context;
import android.content.Intent;
import android.support.v4.content.ContextCompat;

import com.robot.tuling.entity.MessageEntity;
import com.robot.tuling.ui.AboutActivity;
import com.robot.tuling.ui.DetailActivity;
import com.robot.tuling.ui.FaceActivity;
import com.robot.tuling.ui.HelpActivity;
import com.robot.tuling.ui.MoodActivity;
import com.robot.tuling.ui.NewsActivity;
import com.robot.tuling.ui.SocketActivity;

public class NavigateManager {

    public static void gotoAboutActivity(Context context) {
        Intent intent = new Intent(context, AboutActivity.class);
        context.startActivity(intent);
    }

    public static void gotoNewsActivity(Context context, MessageEntity messageEntity) {
        Intent intent = new Intent(context, NewsActivity.class);
        intent.putExtra("messageEntity", messageEntity);
        context.startActivity(intent);
    }

    public static void gotoDetailActivity(Context context, String url) {
        Intent intent = new Intent(context, DetailActivity.class);
        intent.putExtra("url", url);
        context.startActivity(intent);
    }

    public static void gotoHelpActivity(Context context) {
        Intent intent = new Intent(context, HelpActivity.class);
        context.startActivity(intent);
    }

    public static void gotoMoodActivity(Context context) {
        Intent intent = new Intent(context, MoodActivity.class);
        context.startActivity(intent);
    }
    public static void gotoSocketActivity(Context context) {
        Intent intent = new Intent(context, SocketActivity.class);
        context.startActivity(intent);
    }
    public static void gotoFaceActivity(Context context) {
        Intent intent = new Intent(context, FaceActivity.class);
        context.startActivity(intent);
    }
}
