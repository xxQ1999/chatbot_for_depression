package com.robot.tuling.ui;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Color;
import android.graphics.DashPathEffect;
import android.os.Bundle;
import android.support.v7.widget.Toolbar;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.ant.liao.GifView;
import com.github.mikephil.charting.animation.Easing;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.charts.PieChart;
import com.github.mikephil.charting.components.Legend;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.data.PieData;
import com.github.mikephil.charting.data.PieDataSet;
import com.github.mikephil.charting.data.PieEntry;
import com.github.mikephil.charting.formatter.PercentFormatter;
import com.github.mikephil.charting.interfaces.datasets.IDataSet;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;
import com.github.mikephil.charting.utils.ColorTemplate;
import com.github.mikephil.charting.utils.Utils;
import com.robot.tuling.R;
import com.robot.tuling.constant.DataBase;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;

public class MoodActivity extends BaseActivity{
    @BindView(R.id.toolbar)
    Toolbar toolbar;

    private PieChart mPieChart;
   // private LineChart mLineChar;
    private int HAPPY=0,SAD=0,DEPRESSION=0,ANGERY=0,SILK=0,TIRED=0,NOTHING=0,ANXIOUS=0;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_mood);
        ButterKnife.bind(this);

        initData();
        initPie();
     //   initLine();
    }

    private void initData() {
        initActionBar();
    }

    private void initActionBar() {
        toolbar.setTitle(getString(R.string.mood_record));
        toolbar.setSubtitle(getString(R.string.app_name));
        toolbar.setSubtitleTextColor(getResources().getColor(R.color.white));
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
    }
/*
    private void initLine(){
        mLineChar = (LineChart) findViewById(R.id.mLineChar);
        //????????????????????????
     //   mLineChar.setOnChartGestureListener(this);
        //????????????????????????
     //   mLineChar.setOnChartValueSelectedListener(this);
        //????????????
        mLineChar.setDrawGridBackground(false);
        //??????????????????
        mLineChar.getDescription().setEnabled(false);
        //????????????????????????
        mLineChar.setTouchEnabled(true);
        //????????????
        mLineChar.setDragEnabled(true);
        //????????????
        mLineChar.setScaleEnabled(true);
        //????????????,???????????????x??????y???????????????
        mLineChar.setPinchZoom(true);

        ArrayList<Entry> values = new ArrayList<Entry>();
        values.add(new Entry(5, 50));
        values.add(new Entry(10, 66));
        values.add(new Entry(15, 120));
        values.add(new Entry(20, 30));
        values.add(new Entry(35, 10));
        values.add(new Entry(40, 110));
        values.add(new Entry(45, 30));
        values.add(new Entry(50, 160));
        values.add(new Entry(100, 30));

        //????????????
        setDataLine(values);
        //????????????
        mLineChar.animateX(2500);
        //??????
        mLineChar.invalidate();
        // ??????????????????
        Legend l = mLineChar.getLegend();
        // ???????????? ...
        l.setForm(Legend.LegendForm.LINE);

        //??????
        List<ILineDataSet> setsFilled = mLineChar.getData().getDataSets();
        for (ILineDataSet iSet : setsFilled) {
            LineDataSet set = (LineDataSet) iSet;
            if (set.isDrawFilledEnabled())
                set.setDrawFilled(false);
            else
                set.setDrawFilled(true);
        }
        mLineChar.invalidate();
    }
*/
    private void initPie(){
        //?????????
        mPieChart = (PieChart) findViewById(R.id.mPieChart);
        mPieChart.setUsePercentValues(true);
        mPieChart.getDescription().setEnabled(false);
        mPieChart.setExtraOffsets(5, 10, 5, 5);

        mPieChart.setDragDecelerationFrictionCoef(0.95f);
        //??????????????????
        mPieChart.setCenterText("?????????"+GetMood());

        mPieChart.setDrawHoleEnabled(true);
        mPieChart.setHoleColor(Color.WHITE);

        mPieChart.setTransparentCircleColor(Color.WHITE);
        mPieChart.setTransparentCircleAlpha(110);

        mPieChart.setHoleRadius(58f);
        mPieChart.setTransparentCircleRadius(61f);

        mPieChart.setDrawCenterText(true);

        mPieChart.setRotationAngle(0);
        // ????????????
        mPieChart.setRotationEnabled(true);
        mPieChart.setHighlightPerTapEnabled(true);

        getRecord();
        //????????????
   //     mPieChart.setOnChartValueSelectedListener(MoodActivity.this);
        //????????????
        ArrayList<PieEntry> entries = new ArrayList<PieEntry>();
        if(HAPPY!=0) entries.add(new PieEntry(HAPPY, "??????"));
        if(NOTHING!=0) entries.add(new PieEntry(NOTHING, "??????"));
        if(SAD!=0) entries.add(new PieEntry(SAD, "??????"));
        if(DEPRESSION!=0) entries.add(new PieEntry(DEPRESSION, "??????"));
        if(ANGERY!=0)  entries.add(new PieEntry(ANGERY, "??????")); // ????????????????????????
        if(ANXIOUS!=0)  entries.add(new PieEntry(ANXIOUS, "??????"));
        if(SILK!=0)  entries.add(new PieEntry(SILK, "??????"));
        if(TIRED!=0)  entries.add(new PieEntry(TIRED, "??????"));

        //????????????
        setData(entries);
        mPieChart.animateY(1400, Easing.EasingOption.EaseInOutQuad);

        Legend l = mPieChart.getLegend();
        l.setVerticalAlignment(Legend.LegendVerticalAlignment.TOP);
        l.setHorizontalAlignment(Legend.LegendHorizontalAlignment.RIGHT);
        l.setOrientation(Legend.LegendOrientation.VERTICAL);
        l.setDrawInside(false);
        l.setXEntrySpace(7f);
        l.setYEntrySpace(0f);
        l.setYOffset(0f);

        // ??????????????????
        mPieChart.setEntryLabelColor(Color.WHITE);
        mPieChart.setEntryLabelTextSize(12f);
        //????????????
        for (IDataSet<?> set : mPieChart.getData().getDataSets()){
            set.setDrawValues(!set.isDrawValuesEnabled());
        }
        mPieChart.invalidate();
        mPieChart.animateXY(1400, 1400);
    }

    private void getRecord(){
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// ???????????????
        String sql = "select * from MoodRecord where mood = '??????'";
        Cursor cursor = db.rawQuery(sql, null);
        HAPPY = cursor.getCount();
        sql =  "select * from MoodRecord where mood = '??????'";
        cursor = db.rawQuery(sql, null);
        NOTHING = cursor.getCount();
        sql =  "select * from MoodRecord where mood = '??????'";
        cursor = db.rawQuery(sql, null);
        SAD = cursor.getCount();
        sql =  "select * from MoodRecord where mood = '??????'";
        cursor = db.rawQuery(sql, null);
        ANGERY = cursor.getCount();
        sql =  "select * from MoodRecord where mood = '??????'";
        cursor = db.rawQuery(sql, null);
        ANXIOUS = cursor.getCount();
        sql =  "select * from MoodRecord where mood = '??????'";
        cursor = db.rawQuery(sql, null);
        SILK = cursor.getCount();
        sql =  "select * from MoodRecord where mood = '??????'";
        cursor = db.rawQuery(sql, null);
        DEPRESSION = cursor.getCount();
        sql =  "select * from MoodRecord where mood = '??????'";
        cursor = db.rawQuery(sql, null);
        TIRED = cursor.getCount();
        cursor.close();
        db.close();
    }
    private void setData(ArrayList<PieEntry> entries) {
        PieDataSet dataSet = new PieDataSet(entries, "????????????");
        dataSet.setSliceSpace(3f);
        dataSet.setSelectionShift(5f);

        //???????????????
        ArrayList<Integer> colors = new ArrayList<Integer>();
        for (int c : ColorTemplate.VORDIPLOM_COLORS)
            colors.add(c);
        for (int c : ColorTemplate.JOYFUL_COLORS)
            colors.add(c);
        for (int c : ColorTemplate.COLORFUL_COLORS)
            colors.add(c);
        for (int c : ColorTemplate.LIBERTY_COLORS)
            colors.add(c);
        for (int c : ColorTemplate.PASTEL_COLORS)
            colors.add(c);
        colors.add(ColorTemplate.getHoloBlue());
        dataSet.setColors(colors);
        PieData data = new PieData(dataSet);
        data.setValueFormatter(new PercentFormatter());
        data.setValueTextSize(11f);
        data.setValueTextColor(Color.WHITE);
        mPieChart.setData(data);
        mPieChart.highlightValues(null);
        //??????
        mPieChart.invalidate();
    }
/*
    private void setDataLine(ArrayList<Entry> values) {
        LineDataSet set1;
        if (mLineChar.getData() != null && mLineChar.getData().getDataSetCount() > 0) {
            set1 = (LineDataSet) mLineChar.getData().getDataSetByIndex(0);
            set1.setValues(values);
            mLineChar.getData().notifyDataChanged();
            mLineChar.notifyDataSetChanged();
        } else {
            // ?????????????????????,?????????????????????
            set1 = new LineDataSet(values, "??????????????????");

            // ??????????????????
            set1.enableDashedLine(10f, 5f, 0f);
            set1.enableDashedHighlightLine(10f, 5f, 0f);
            set1.setColor(Color.BLACK);
            set1.setCircleColor(Color.BLACK);
            set1.setLineWidth(1f);
            set1.setCircleRadius(3f);
            set1.setDrawCircleHole(false);
            set1.setValueTextSize(9f);
            set1.setDrawFilled(true);
            set1.setFormLineWidth(1f);
            set1.setFormLineDashEffect(new DashPathEffect(new float[]{10f, 5f}, 0f));
            set1.setFormSize(15.f);

            if (Utils.getSDKInt() >= 18) {
                // ?????????????????????18??????
                //Drawable drawable = ContextCompat.getDrawable(this, R.mipmap.ic_launcher);
                //set1.setFillDrawable(drawable);
                set1.setFillColor(Color.parseColor("#43aea8"));
            } else {
                set1.setFillColor(Color.BLACK);
            }
            ArrayList<ILineDataSet> dataSets = new ArrayList<ILineDataSet>();
            //???????????????
            dataSets.add(set1);

            //????????????????????????????????????
            LineData data = new LineData(dataSets);

            //????????????
            mLineChar.setData(data);
        }
    }
    */
    public String getMyDate(){
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy???MM???dd???");// HH:mm:ss
    //??????????????????
        Date date = new Date(System.currentTimeMillis());
        return simpleDateFormat.format(date);
    }

    public String GetMood(){
        //????????????
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// ???????????????
        String sql = "select * from MoodRecord where date = '"+getMyDate()+"'";
        String mood = "";
        Cursor cursor = db.rawQuery(sql, null);
        if (cursor.getCount()==0) return "?????????";
        while (cursor.moveToNext()) {
            mood = cursor.getString(0);
            break;
        }
        return mood;
    }
}
