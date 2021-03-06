package com.robot.tuling.ui;

import com.robot.tuling.constant.DataBase;
import com.robot.tuling.constant.JokeParameter;
import com.robot.tuling.constant.Parameters;

import android.content.ContentValues;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.icu.text.UnicodeSetSpanner;
import android.os.Bundle;
import android.os.Looper;
import android.os.StrictMode;
import android.provider.Settings;
import android.support.v7.widget.Toolbar;
import android.util.JsonReader;
import android.util.Log;
import android.view.View;
import android.widget.AbsListView;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ListView;
import android.widget.RelativeLayout;
import android.widget.Toast;

import com.robot.tuling.R;
import com.robot.tuling.adapter.ChatMessageAdapter;
import com.robot.tuling.constant.TulingParams;
import com.robot.tuling.control.RetrofitApi;
import com.robot.tuling.entity.MessageEntity;
import com.robot.tuling.util.IsNullOrEmpty;
import com.robot.tuling.util.KeyBoardUtil;
import com.robot.tuling.util.TimeUtil;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.IOException;
import java.io.Reader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

import butterknife.BindView;
import butterknife.ButterKnife;
import io.reactivex.android.schedulers.AndroidSchedulers;
import io.reactivex.schedulers.Schedulers;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.FormBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import retrofit2.Retrofit;
import retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory;
import retrofit2.converter.gson.GsonConverterFactory;
import retrofit2.http.Url;

public class HelpActivity extends BaseActivity {

    @BindView(R.id.toolbar)
    Toolbar toolbar;
    @BindView(R.id.lv_message2)
    ListView lvMessage2;
    @BindView(R.id.iv_send_msg2)
    ImageView ivSendMsg2;
    @BindView(R.id.et_msg2)
    EditText etMsg2;
    @BindView(R.id.rl_msg2)
    RelativeLayout rlMsg2;

    private final int MOOD_CHOOSE = 1, YES_NO = 2, NOTHING = 3 ;
    private List<MessageEntity> msgList = new ArrayList<>();
    private ChatMessageAdapter msgAdapter;
    private int now_state = 0;
    private Parameters seq = new Parameters();
    private Parameters emoji = new Parameters();
    private RelativeLayout rlayout;
    private ImageView send;
    private EditText input;
    private Button btnYes,btnNo,btnNothing;
    private Button btnAnxious, btnRegret, btnLonely, btnRelationship, btnSleepy, btnAngry,btnFine;
    private Button btn1,btn2,btn3,btn4,btn5,btn6,btn7,btn8;
    private KeyBoardUtil keyBoardUtil;
    private int news=0;
    private String A,B,C,D,E,mood;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_help);
        ButterKnife.bind(this);

        initView();
        initActionBar();
        initData();
        initListener();
        FirstMood();
    }

    private void initView(){
        rlayout = (RelativeLayout) findViewById(R.id.rl_msg2);
        send = (ImageView) findViewById(R.id.iv_send_msg2);
        input = (EditText) findViewById(R.id.et_msg2);
        btnNo = (Button) findViewById(R.id.btn_no);
        btnYes = (Button) findViewById(R.id.btn_yes);
        btnAnxious = (Button) findViewById(R.id.btn_anxious);
        btnRegret = (Button) findViewById(R.id.btn_regret);
        btnLonely = (Button) findViewById(R.id.btn_lonely);
        btnRelationship = (Button) findViewById(R.id.btn_ship);
        btnSleepy = (Button) findViewById(R.id.btn_sleep);
        btnAngry = (Button) findViewById(R.id.btn_angry);
        btnFine = (Button) findViewById(R.id.btn_fine);
        btnNothing = (Button) findViewById(R.id.btn_nothing);
        btn1 = (Button) findViewById(R.id.btn_1);
        btn2 = (Button) findViewById(R.id.btn_2);
        btn3 = (Button) findViewById(R.id.btn_3);
        btn4 = (Button) findViewById(R.id.btn_4);
        btn5 = (Button) findViewById(R.id.btn_5);
        btn6 = (Button) findViewById(R.id.btn_6);
        btn7 = (Button) findViewById(R.id.btn_7);
        btn8 = (Button) findViewById(R.id.btn_8);
    }
    private void initActionBar() {
        toolbar.setTitle(getString(R.string.help));
        toolbar.setSubtitle(getString(R.string.app_name));
        toolbar.setSubtitleTextColor(getResources().getColor(R.color.white));
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
    }
    private void initData() {
        if (msgList.size() == 0) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_LEFT, TimeUtil.getCurrentTimeMillis());
            if(!JudgeIfTodayRecord()) {
                entity.setText("??????????????????????????????~"+emoji.getHappyEmoji());
                msgList.add(entity);
            }else{
                if(!JudgeSad()){
                    entity.setText("??????????????????????????????~"+emoji.getHeartEmoji());
                    msgList.add(entity);
                }
            }
        }
        msgAdapter = new ChatMessageAdapter(this, msgList);
        lvMessage2.setAdapter(msgAdapter);
        lvMessage2.setSelection(msgAdapter.getCount());
        now_state = 0;
        if(JudgeIfTodayRecord()) {
            if (JudgeSad()) {
                setLeft("??????????????????~?????????????????????????????????"+emoji.getHappyEmoji()); //????????????????????????????????????????????????:)
                HideInput();
                ShowYesOrNoBtn("????????????"+emoji.getHappyEmoji(), "????????????"+emoji.getNothingEmoji());
                return ;
            }
        }
        setLeft("?????????????????????????????????~"+emoji.getHappyEmoji());

    }

    private void initListener() {
        ivSendMsg2.setOnClickListener(onClickListener);
        lvMessage2.setOnScrollListener(new AbsListView.OnScrollListener() {
            @Override
            public void onScrollStateChanged(AbsListView view, int scrollState) {
                KeyBoardUtil.hideKeyboard(mActivity);
            }

            @Override
            public void onScroll(AbsListView view, int firstVisibleItem, int visibleItemCount, int totalItemCount) {
            }
        });
        btnYes.setOnClickListener(onClickListener);
        btnNo.setOnClickListener(onClickListener);
        btnNothing.setOnClickListener(onClickListener);
        btnAnxious.setOnClickListener(onClickListener);
        btnRegret.setOnClickListener(onClickListener);
        btnLonely.setOnClickListener(onClickListener);
        btnRelationship.setOnClickListener(onClickListener);
        btnSleepy.setOnClickListener(onClickListener);
        btnAngry.setOnClickListener(onClickListener);
        btnFine.setOnClickListener(onClickListener);
        btn1.setOnClickListener(onClickListener);
        btn2.setOnClickListener(onClickListener);
        btn3.setOnClickListener(onClickListener);
        btn4.setOnClickListener(onClickListener);
        btn5.setOnClickListener(onClickListener);
        btn6.setOnClickListener(onClickListener);
        btn7.setOnClickListener(onClickListener);
        btn8.setOnClickListener(onClickListener);
    }

    View.OnClickListener onClickListener = new View.OnClickListener() {
        @Override
        public void onClick(View v) {
            HideBtn();
            switch (v.getId()){
                case R.id.iv_send_msg2:
                    SendAction();
                    break;
                case R.id.btn_angry:
                    now_state = 46;
                    setRight(btnAngry.getText().toString());
                    Help(46);
                    break;
                case R.id.btn_anxious:
                    now_state = 4;
                    setRight(btnAnxious.getText().toString());
                    Help(4);
                    break;
                case R.id.btn_lonely:
                    now_state = 17;
                    setRight(btnLonely.getText().toString());
                    Help(17);
                    break;
                case R.id.btn_regret:
                    now_state = 10;
                    setRight(btnRegret.getText().toString());
                    Help(10);
                    break;
                case R.id.btn_ship:
                    now_state = 19;
                    setRight(btnRelationship.getText().toString());
                    Help(19);
                    break;
                case R.id.btn_sleep:
                    now_state = 40;
                    setRight(btnSleepy.getText().toString());
                    Help(40);
                    break;
                case R.id.btn_fine:
                    now_state = 0;
                    setRight(btnFine.getText().toString());
                    setLeft("?????????????????????????????????????????????????????????~"+emoji.getHappyEmoji());
                    break;
                case R.id.btn_yes:
                    YesAction();
                    break;
                case R.id.btn_no:
                    NoAction();
                    break;
                case R.id.btn_nothing:
                    NothingAction();
                    break;
                case R.id.btn_1: mood=btn1.getText().toString();ShowInput();MoodRecord();setRight(emoji.getHappyEmoji());setLeft("??????????????????????????????~");break;
                case R.id.btn_2: mood=btn2.getText().toString();ShowInput();MoodRecord();setRight(emoji.getNothingEmoji());setLeft("?????????????????????????????????");break;
                case R.id.btn_3: mood=btn3.getText().toString();ShowInput();MoodRecord();now_state=1;setRight(emoji.getSadEmoji());Help(now_state);break;
                case R.id.btn_4: mood=btn4.getText().toString();ShowInput();MoodRecord();now_state=1;setRight(emoji.getSadEmoji());Help(now_state);break;
                case R.id.btn_5: mood=btn5.getText().toString();ShowInput();MoodRecord();now_state=4;setRight(emoji.getSadEmoji());Help(now_state);break;
                case R.id.btn_6: mood=btn6.getText().toString();ShowInput();MoodRecord();now_state=46;setRight(emoji.getAngryEmoji());Help(now_state);break;
                case R.id.btn_7: mood=btn7.getText().toString();ShowInput();MoodRecord();now_state=1;setRight(emoji.getAfraidEmoji());Help(now_state);break;
                case R.id.btn_8: mood=btn8.getText().toString();ShowInput();MoodRecord();now_state=1;setRight(emoji.getDisguseEmoji());Help(now_state);break;
            }
        }
    };

    public void SendAction(){
        if (!IsNullOrEmpty.isEmpty(etMsg2.getText().toString().trim())) {
            String input = etMsg2.getText().toString().trim();
            setRight();
            switch (now_state){
                case 0:
                case 1:
                    if(input.contains("??????")) { TellJoke(); break; }
                    else now_state++;Help(now_state);
                    break;
                case 28: now_state++;Help(29);A=input;break;
                case 35: now_state++;B=input;Help(now_state);break;
                case 36: now_state++;C=input;Help(now_state);break;
                case 37: now_state++;D=input;Help(now_state);break;
                case 38: now_state++;E=input;Help(now_state);break;
                case 47: now_state++;A=input;Help(now_state);break;
                case 72: now_state++;A=input;Help(now_state);break;
                case 73: now_state++;B=input;Help(now_state);break;
                default: now_state++;Help(now_state);break;
            }
        }
    }

    public String getMyDate(){
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy???MM???dd???");// HH:mm:ss
//??????????????????
        Date date = new Date(System.currentTimeMillis());
        return simpleDateFormat.format(date);
    }


    public void TellJoke(){
        //?????????
        RequestJoke();
        Toast.makeText(mContext,"!!",Toast.LENGTH_LONG).show();
    }

    private void RequestJoke()  {
        Thread accessWebServiceThread = new Thread(new WebServiceHandler());
        accessWebServiceThread.start();
           /* OkHttpClient client = new OkHttpClient();//??????OkHttpClient??????
            Request request = new Request.Builder()
                    .url(JokeParameter.JOKE_URL+"?key="+JokeParameter.JOKE_KEY)//?????????????????????????????????????????????????????????
                    .build();//??????Request ??????
            Response response = null;
            response = client.newCall(request).execute();//??????Response ??????
            if (response.isSuccessful()) {
                Log.d("kwwl","response.code()=="+response.code());
                Log.d("kwwl","response.message()=="+response.message());
                Log.d("kwwl","res=="+response.body());
                Toast.makeText(this,"!",Toast.LENGTH_LONG).show();
                //??????????????????????????????????????????UI??????????????????handler?????????UI?????????*/
         /*    OkHttpClient mOkHttpClient = new OkHttpClient.Builder()
                     .connectTimeout(10, TimeUnit.SECONDS)
                     .readTimeout(10, TimeUnit.SECONDS)
                     .build();
            Request request =  new Request.Builder()
                    .get()
                    .url(JokeParameter.JOKE_URL+"?key="+JokeParameter.JOKE_KEY)
                    .build();

            Call call = mOkHttpClient.newCall(request);
            try{
                Response response = call.execute();
                Toast.makeText(mContext,response.message().toString(),Toast.LENGTH_LONG).show();
            }catch (Exception e){
                ;

                Toast.makeText(mContext,"??",Toast.LENGTH_LONG).show();
            }

*/
    }

    class WebServiceHandler implements Runnable{
        @Override
        public void run() {
            Looper.prepare();
            try {
                //  StrictMode.ThreadPolicy policy=new StrictMode.ThreadPolicy.Builder().permitAll().build();
                //  StrictMode.setThreadPolicy(policy);
                OkHttpClient client = new OkHttpClient();
                URL url = new URL(JokeParameter.JOKE_URL + "?key=" + JokeParameter.JOKE_KEY);
                Request request = new Request.Builder()
                        .url(url)
                        .get()
                        .build();
                final Call call = client.newCall(request);
                Response response = call.execute();
                //System.out.println(response.body().string());
                String content = response.body().string();
                System.out.println(content);
                int idBegin=0,idEnd=0;
                for(int i=0;i<content.length();i++)
                {
                    if(content.charAt(i)=='[') {
                        idBegin = i + 13;
                    }
                    if(idBegin!=0){
                        if(content.charAt(i)=='h'&&content.charAt(i+1)=='a'&&content.charAt(i+2)=='s'&&content.charAt(i+3)=='h'&&content.charAt(i+4)=='I'
                            &&content.charAt(i+5)=='d') {
                            idEnd = i - 4;
                            break;
                        }
                    }
                }
                String x = "";
                for(int i=idBegin;i<=idEnd;i++)
                    x+=content.charAt(i);
                setLeft(x);
               // Toast.makeText(mContext,joke.optString("content"),Toast.LENGTH_LONG).show();
            }catch (Exception e){
                Log.e("url",e.getMessage());
            }
            Looper.loop();
        }

    }

    public boolean JudgeSad(){
        //????????????
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// ???????????????
        String sql = "select * from MoodRecord where date = '"+getMyDate()+"' and mood = '??????'";
        Cursor cursor = db.rawQuery(sql, null);
        if(cursor.getCount()==0) {cursor.close();db.close();return true;}
        else {cursor.close();db.close();return false;}
    }
    public void YesAction(){
        String yes = btnYes.getText().toString().trim();
        setRight(yes);
        HideBtn();
        switch (now_state){
            case 0: TellJoke();ShowInput();break;
            case 2: now_state = 47;Help(47);break;
            case 5: now_state= 47;Help(47);break;
            case 18: now_state= 47;Help(47);break;
            case 23: now_state = 24;Help(24);break;
            case 31:
            case 32:
            case 33: now_state++;Help(now_state);break;
            case 40: now_state=41;Help(now_state);break;
            case 46: now_state=47;Help(now_state); break;
            case 49: now_state=50;Help(now_state);break;
            case 52: now_state=53;Help(now_state);break;
            case 54: now_state=55;Help(now_state);break;
            case 56: now_state=57;Help(now_state);break;
            case 61: now_state=64;Help(now_state);break;
        }
    }
    public void NoAction(){
        String no = btnNo.getText().toString().trim();
        setRight(no);
        HideBtn();
        switch (now_state){
            case 0: setLeft("????????????????????????????????????~");setLeft("????????????????????????????????????????????????????????????~");ShowInput();break;
            case 2: now_state = 3;Help(3);break;
            case 5: now_state=6;Help(6);break;
            case 19: now_state=65;Help(65);break;
            case 23: now_state = 25;Help(25);break;
            case 31:
            case 32:
            case 33: now_state++;Help(now_state);break;
            case 40: now_state=43;Help(now_state);break;
            case 46: now_state=65;Help(now_state); break;
            case 49: now_state=51;Help(now_state);break;
            case 52: now_state=54;Help(now_state);break;
            case 54: now_state=56;Help(now_state);break;
            case 56: now_state=58;Help(now_state);break;
            case 61: now_state=62;Help(now_state);break;
        }
    }

    public void NothingAction(){
        HideBtn();
        setRight(btnNothing.getText().toString());
        switch(now_state){
            case 24: if(news==1) now_state = 25;
            else now_state = 26;
                Help(now_state);break;
            case 25: if(news==1) now_state = 24;
            else now_state = 26;
                Help(now_state);break;
            default: now_state++;Help(now_state);
                break;
        }
    }
    public void HideInput(){
        send.setVisibility(View.GONE);
        input.setVisibility(View.GONE);
        keyBoardUtil.hideKeyboard(HelpActivity.this);
    }

    public void ShowInput(){
        send.setVisibility(View.VISIBLE);
        input.setVisibility(View.VISIBLE);
    }

    public void HideBtn() {
        btnYes.setVisibility(View.GONE);
        btnNo.setVisibility(View.GONE);
        btnNothing.setVisibility(View.GONE);
        btnAngry.setVisibility(View.GONE);
        btnAnxious.setVisibility(View.GONE);
        btnRegret.setVisibility(View.GONE);
        btnRelationship.setVisibility(View.GONE);
        btnLonely.setVisibility(View.GONE);
        btnSleepy.setVisibility(View.GONE);
        btnFine.setVisibility(View.GONE);
        btn1.setVisibility(View.GONE);
        btn2.setVisibility(View.GONE);
        btn3.setVisibility(View.GONE);
        btn4.setVisibility(View.GONE);
        btn5.setVisibility(View.GONE);
        btn6.setVisibility(View.GONE);
        btn7.setVisibility(View.GONE);
        btn8.setVisibility(View.GONE);
    }

    public void ShowYesOrNoBtn(String yes,String no){
        btnYes.setVisibility(View.VISIBLE);
        btnNo.setVisibility(View.VISIBLE);
        btnYes.setText(yes);
        btnNo.setText(no);
    }

    public void ShowNothingBtn(String nothing){
        btnNothing.setVisibility(View.VISIBLE);
        btnNothing.setText(nothing);
    }

    public void ShowMoodBtn(){
        btn1.setVisibility(View.VISIBLE);
        btn2.setVisibility(View.VISIBLE);
        btn3.setVisibility(View.VISIBLE);
        btn4.setVisibility(View.VISIBLE);
        btn5.setVisibility(View.VISIBLE);
        btn6.setVisibility(View.VISIBLE);
        btn7.setVisibility(View.VISIBLE);
    }

    public void ShowProblemBtn(){
        btnAngry.setVisibility(View.VISIBLE);
        btnAnxious.setVisibility(View.VISIBLE);
        btnRegret.setVisibility(View.VISIBLE);
        btnRelationship.setVisibility(View.VISIBLE);
        btnLonely.setVisibility(View.VISIBLE);
        btnSleepy.setVisibility(View.VISIBLE);
        btnFine.setVisibility(View.VISIBLE);
    }
    //????????????
    public void setRight() {
        String msg = etMsg2.getText().toString().trim();
        if (!IsNullOrEmpty.isEmpty(msg)) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_RIGHT, TimeUtil.getCurrentTimeMillis(), msg);
            msgList.add(entity);
            msgAdapter.notifyDataSetChanged();
            etMsg2.setText("");
        }
    }

    //????????????
    public void setRight(String msg) {
        if (!IsNullOrEmpty.isEmpty(msg)) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_RIGHT, TimeUtil.getCurrentTimeMillis(), msg);
            msgList.add(entity);
            msgAdapter.notifyDataSetChanged();
            etMsg2.setText("");
        }
    }

    //???????????????
    public void setLeft(String msg){
        MessageEntity entity = new MessageEntity();
        entity.setTime(TimeUtil.getCurrentTimeMillis());
        entity.setType(ChatMessageAdapter.TYPE_LEFT);
        entity.setText(msg);
        msgList.add(entity);
        msgAdapter.notifyDataSetChanged();
    }

    public boolean JudgeIfTodayRecord(){
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// ???????????????
        String sql = "select * from MoodRecord where date = '"+getMyDate()+"'";
        Cursor cursor = db.rawQuery(sql, null);
        if(cursor.getCount()==0) {db.close();cursor.close();return false;}
        else {db.close();cursor.close();return true;}
    }
    public void FirstMood(){
        if(JudgeIfTodayRecord()) return;
        HideInput();
        setLeft("??????~???????????????????????????????????????????????????\n(*???-???*)");
        ShowMoodBtn();
    }
    public void MoodRecord(){
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getWritableDatabase();// ???????????????
        ContentValues values = new ContentValues();
        values.put("date", getMyDate());
        values.put("mood", mood);
        db.insert("MoodRecord", null, values);
        Toast.makeText(this, "????????????", Toast.LENGTH_LONG).show();
        db.close();
    }
    public void Help(int state){
        switch (now_state){
            case 0: break;
            case 1:
                setLeft("??????????????????????????????????????????????????????");
                break;
            case 2:
                setLeft("????????????????????????????????????");
                HideInput();
                ShowYesOrNoBtn("????????????","?????????");
                break;
            case 3: setLeft(seq.MoodTalk[4]);HideInput();ShowProblemBtn();break;
            case 4: setLeft(seq.MoodTalk[5]);ShowNothingBtn("??????");break;
            case 5: setLeft(seq.MoodTalk[6]);ShowYesOrNoBtn("????????????","????????????");break;
            case 6: setLeft(seq.MoodTalk[7]);ShowNothingBtn("??????");break;
            case 7: setLeft(seq.MoodTalk[8]);setLeft(seq.MoodTalk[9]);ShowNothingBtn("??????");break;
            case 8: setLeft(seq.MoodTalk[10]);setLeft(seq.MoodTalk[11]);setLeft(seq.MoodTalk[12]);ShowNothingBtn("?????????");break;
            case 9: setLeft(seq.MoodTalk[13]);ShowInput();now_state=0;break; //Ask=0;
            case 10: setLeft(seq.MoodTalk[14]);setLeft(seq.MoodTalk[15]);setLeft(seq.MoodTalk[16]);ShowNothingBtn("???????????????");break;
            case 11: setLeft(seq.MoodTalk[17]);setLeft(seq.MoodTalk[18]);ShowNothingBtn("??????");break;
            case 12: setLeft(seq.MoodTalk[19]);setLeft(seq.MoodTalk[20]);ShowNothingBtn("??????");break;
            case 13: setLeft(seq.MoodTalk[21]);setLeft(seq.MoodTalk[22]);ShowNothingBtn("?????????");break;
            case 14: setLeft(seq.MoodTalk[23]);setLeft(seq.MoodTalk[24]);setLeft(seq.MoodTalk[25]);ShowNothingBtn("????????????");break;
            case 15: setLeft(seq.MoodTalk[26]);ShowNothingBtn("??????");break;
            case 16: setLeft(seq.MoodTalk[27]);ShowInput();now_state=0;break;
            case 17: setLeft(seq.MoodTalk[28]);setLeft(seq.MoodTalk[29]);setLeft(seq.MoodTalk[30]);ShowNothingBtn("??????????????????");break;
            case 18: setLeft(seq.MoodTalk[31]);ShowYesOrNoBtn("????????????","????????????");break;

            case 19: setLeft(seq.MoodTalk[32]);ShowNothingBtn("??????");break;
            case 20: setLeft(seq.MoodTalk[33]); setLeft(seq.MoodTalk[34]);ShowNothingBtn("??????????????????");break;
            case 21: setLeft(seq.MoodTalk[35]);ShowNothingBtn("??????");break;
            case 22: setLeft(seq.MoodTalk[36]);ShowNothingBtn("?????????????????????");break;
            case 23: setLeft(seq.MoodTalk[37]);ShowYesOrNoBtn("?????????","?????????");news=0;break;
            case 24: setLeft(seq.MoodTalk[38]);if(news==0) {ShowNothingBtn("??????????????????");news++;}
            else{ShowNothingBtn("??????????????????");news++;} break;
            case 25: setLeft(seq.MoodTalk[39]); if(news==0) {ShowNothingBtn("??????????????????");news++;}
            else {ShowNothingBtn("??????????????????");news++;} break;
            case 26: setLeft(seq.MoodTalk[40]);ShowNothingBtn("?????????");news=0;break;
            case 27: setLeft(seq.MoodTalk[41]); setLeft(seq.MoodTalk[42]); HideBtn(); ShowInput();break;
            case 28: setLeft(seq.MoodTalk[43]); break;
            case 29: setLeft(seq.MoodTalk[44]); setLeft(seq.MoodTalk[45]); break;
            case 30: setLeft(seq.MoodTalk[46]); break;
            case 31: setLeft(seq.MoodTalk[47]);HideInput();ShowYesOrNoBtn("???","??????");break;
            case 32: setLeft(seq.MoodTalk[48]);ShowYesOrNoBtn("???","??????");break;
            case 33: setLeft(seq.MoodTalk[49]);ShowYesOrNoBtn("?????????","??????");break;
            case 34: setLeft(seq.MoodTalk[50]); setLeft(seq.MoodTalk[51]); setLeft(seq.MoodTalk[52]);ShowNothingBtn("?????????");break;
            case 35: setLeft(seq.MoodTalk[53]); HideBtn(); ShowInput();break;
            case 36: setLeft(seq.MoodTalk[54]); break;
            case 37: setLeft(seq.MoodTalk[55]); break;
            case 38: setLeft(seq.MoodTalk[56]); break;
            case 39: setLeft(seq.MoodTalk[57]); setLeft("?????????????????????"+A+"????????????????????????" +B+"???"+C+"???"+D+"???"+E+"???"); setLeft(seq.MoodTalk[59]); setLeft(seq.MoodTalk[60]);
                ShowInput();now_state=0;break;

            case 40:  setLeft(seq.MoodTalk[61]); setLeft(seq.MoodTalk[62]); HideInput();ShowYesOrNoBtn("????????????","????????????"); break;
            case 41:  setLeft(seq.MoodTalk[63]); setLeft(seq.MoodTalk[64]); ShowNothingBtn("??????");break;
            case 42:  setLeft(seq.MoodTalk[65]); setLeft(seq.MoodTalk[66]); setLeft(seq.MoodTalk[67]); setLeft(seq.MoodTalk[68]); setLeft(seq.MoodTalk[69]);
                setLeft(seq.MoodTalk[70]); setLeft(seq.MoodTalk[71]); break;
            case 43:  setLeft(seq.MoodTalk[72]);  setLeft(seq.MoodTalk[73]);ShowNothingBtn("????????????");break;
            case 44:  setLeft(seq.MoodTalk[74]);  setLeft(seq.MoodTalk[75]);ShowNothingBtn("???????????????");break;
            case 45:  setLeft(seq.MoodTalk[76]); setLeft(seq.MoodTalk[77]);ShowInput();now_state=0;break;

            case 46:  setLeft(seq.MoodTalk[78]); ShowYesOrNoBtn("????????????","????????????");break;

            case 47: setLeft(seq.CBT[0]);setLeft(seq.CBT[1]);ShowInput(); break;
            case 48: setLeft(seq.CBT[2]);HideInput();ShowNothingBtn("????????????????????????");break;
            case 49: setLeft(seq.CBT[3]);setLeft(seq.CBT[4]);setLeft(seq.CBT[5]); ShowYesOrNoBtn("??????","?????????");break;
            case 50: setLeft(seq.CBT[6]);ShowNothingBtn("??????");break;
            case 51: setLeft(seq.CBT[7]);ShowNothingBtn("???????????????");break;
            case 52: setLeft(seq.CBT[8]);setLeft(seq.CBT[9]); ShowYesOrNoBtn("??????","?????????");break;
            case 53: setLeft(seq.CBT[10]); now_state=53;
            case 54: setLeft(seq.CBT[11]); now_state=54;ShowYesOrNoBtn("??????","?????????");break;
            case 55: setLeft(seq.CBT[12]); Toast.makeText(this,"!!",Toast.LENGTH_LONG).show();ShowNothingBtn("??????");break;
            case 56: setLeft(seq.CBT[13]); ShowYesOrNoBtn("??????","?????????");break;
            case 57: setLeft(seq.CBT[14]); setLeft(seq.CBT[15]); ShowNothingBtn("??????");break;
            case 58: setLeft(seq.CBT[16]); ShowNothingBtn("?????????????????????");break;
            case 59: setLeft(seq.CBT[17]); ShowNothingBtn("??????~");break;
            case 60: setLeft(seq.CBT[18]); setLeft("????????????????????????"+A); ShowInput(); break;
            case 61: setLeft(seq.CBT[19]); HideInput();ShowYesOrNoBtn("?????????","?????????????????????");break;
            case 62: setLeft(seq.CBT[20]); ShowNothingBtn("????????????");break;
            case 63: setLeft(seq.CBT[21]); setLeft(seq.CBT[22]);ShowNothingBtn("????????????"); break;
            case 64: setLeft(seq.CBT[23]); now_state=0;ShowInput();HideBtn();break;


            case 65: setLeft(seq.CTF[0]); setLeft(seq.CTF[1]); setLeft(seq.CTF[2]); setLeft(seq.CTF[3]); ShowNothingBtn("?????????");break;
            case 66: setLeft(seq.CTF[4]); setLeft(seq.CTF[5]); ShowNothingBtn("??????????????????");break;
            case 67: setLeft(seq.CTF[6]); setLeft(seq.CTF[7]); ShowNothingBtn("????????????");break;
            case 68: setLeft(seq.CTF[8]); setLeft(seq.CTF[9]);setLeft(seq.CTF[10]); ShowNothingBtn("??????????????????????????????");break;
            case 69: setLeft(seq.CTF[11]); ShowInput(); break;
            case 70: setLeft(seq.CTF[12]);setLeft(seq.CTF[13]);setLeft(seq.CTF[14]);setLeft(seq.CTF[15]);setLeft(seq.CTF[16]);HideInput();ShowNothingBtn("???");break;
            case 71: setLeft(seq.CTF[17]); ShowNothingBtn("??????");break;
            case 72: setLeft(seq.CTF[18]);setLeft(seq.CTF[19]);setLeft(seq.CTF[20]); ShowInput(); break;
            case 73: setLeft(seq.CTF[21]); break;
            case 74: setLeft("??????????????????????????????"+B+"????????????????????????????????????"); break;
            case 75: setLeft("??????????????????????????????????????????????????????"+A+"????????????????????????????????????????????????????????????????????????????????????");setLeft(seq.CTF[24]); break;
            case 76: setLeft(seq.CTF[25]);setLeft(seq.CTF[26]); now_state=0;break;
        }
    }


}
