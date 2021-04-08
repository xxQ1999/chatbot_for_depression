package com.robot.tuling.constant;

import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.widget.Toast;

public class DataBase extends SQLiteOpenHelper {

    public static final String CREATE_MoodRecord = "create table MoodRecord ("
            + "mood string ,"
            + "date string)";
    public static final String CREATE_ChatRecord = "create table ChatRecord ("
            + "seq string ,"
            + "owner bool,"
            + "date string)";
    public static final String CREATE_UserMessage = "create table UserMessage("
            + "ip string)";
    private Context mContext;

    public DataBase(Context context, String name, SQLiteDatabase.CursorFactory factory, int version) {
        super(context, name, factory, version);
        mContext = context;
    }

    @Override
    public void onCreate(SQLiteDatabase db) {
        db.execSQL(CREATE_MoodRecord);
        db.execSQL(CREATE_ChatRecord);
        db.execSQL(CREATE_UserMessage);
        //   Toast.makeText(mContext,"Create succeed",Toast.LENGTH_SHORT).show();
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("drop table if exists MoodRecord");
        db.execSQL("drop table if exists UserMessage");
        Toast.makeText(mContext,"Update",Toast.LENGTH_SHORT).show();
        onCreate(db);

    }
}