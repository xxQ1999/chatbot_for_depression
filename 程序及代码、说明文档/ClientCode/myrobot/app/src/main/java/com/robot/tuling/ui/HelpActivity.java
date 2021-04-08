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
                entity.setText("嘿，很高兴你能想起我~"+emoji.getHappyEmoji());
                msgList.add(entity);
            }else{
                if(!JudgeSad()){
                    entity.setText("嘿，很高兴你能想起我~"+emoji.getHeartEmoji());
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
                setLeft("啊哈，小同学~想听个笑话乐呵一下不？"+emoji.getHappyEmoji()); //心情不好哦？要不要听我讲个笑话呀:)
                HideInput();
                ShowYesOrNoBtn("好啊好啊"+emoji.getHappyEmoji(), "不想听诶"+emoji.getNothingEmoji());
                return ;
            }
        }
        setLeft("希望今天的你也是快乐的~"+emoji.getHappyEmoji());

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
                    setLeft("幸福有的时候也很简单，那我们下次再见吧~"+emoji.getHappyEmoji());
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
                case R.id.btn_1: mood=btn1.getText().toString();ShowInput();MoodRecord();setRight(emoji.getHappyEmoji());setLeft("哈哈，你开心我也开心~");break;
                case R.id.btn_2: mood=btn2.getText().toString();ShowInput();MoodRecord();setRight(emoji.getNothingEmoji());setLeft("笑口常开，好彩自然来。");break;
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
                    if(input.contains("笑话")) { TellJoke(); break; }
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
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy年MM月dd日");// HH:mm:ss
//获取当前时间
        Date date = new Date(System.currentTimeMillis());
        return simpleDateFormat.format(date);
    }


    public void TellJoke(){
        //讲笑话
        RequestJoke();
        Toast.makeText(mContext,"!!",Toast.LENGTH_LONG).show();
    }

    private void RequestJoke()  {
        Thread accessWebServiceThread = new Thread(new WebServiceHandler());
        accessWebServiceThread.start();
           /* OkHttpClient client = new OkHttpClient();//创建OkHttpClient对象
            Request request = new Request.Builder()
                    .url(JokeParameter.JOKE_URL+"?key="+JokeParameter.JOKE_KEY)//请求接口。如果需要传参拼接到接口后面。
                    .build();//创建Request 对象
            Response response = null;
            response = client.newCall(request).execute();//得到Response 对象
            if (response.isSuccessful()) {
                Log.d("kwwl","response.code()=="+response.code());
                Log.d("kwwl","response.message()=="+response.message());
                Log.d("kwwl","res=="+response.body());
                Toast.makeText(this,"!",Toast.LENGTH_LONG).show();
                //此时的代码执行在子线程，修改UI的操作请使用handler跳转到UI线程。*/
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
        //检测难受
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// 打开数据库
        String sql = "select * from MoodRecord where date = '"+getMyDate()+"' and mood = '开心'";
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
            case 0: setLeft("那我就藏着下次讲给你听吧~");setLeft("如果想听笑话的话，就告诉我“讲个笑话”哦~");ShowInput();break;
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
    //用户输入
    public void setRight() {
        String msg = etMsg2.getText().toString().trim();
        if (!IsNullOrEmpty.isEmpty(msg)) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_RIGHT, TimeUtil.getCurrentTimeMillis(), msg);
            msgList.add(entity);
            msgAdapter.notifyDataSetChanged();
            etMsg2.setText("");
        }
    }

    //选项发送
    public void setRight(String msg) {
        if (!IsNullOrEmpty.isEmpty(msg)) {
            MessageEntity entity = new MessageEntity(ChatMessageAdapter.TYPE_RIGHT, TimeUtil.getCurrentTimeMillis(), msg);
            msgList.add(entity);
            msgAdapter.notifyDataSetChanged();
            etMsg2.setText("");
        }
    }

    //机器人回答
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
        SQLiteDatabase db = dbHelper.getReadableDatabase();// 打开数据库
        String sql = "select * from MoodRecord where date = '"+getMyDate()+"'";
        Cursor cursor = db.rawQuery(sql, null);
        if(cursor.getCount()==0) {db.close();cursor.close();return false;}
        else {db.close();cursor.close();return true;}
    }
    public void FirstMood(){
        if(JudgeIfTodayRecord()) return;
        HideInput();
        setLeft("哈喽~又是新的一天，今天的心情怎么样呢？\n(*＾-＾*)");
        ShowMoodBtn();
    }
    public void MoodRecord(){
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase db = dbHelper.getWritableDatabase();// 打开数据库
        ContentValues values = new ContentValues();
        values.put("date", getMyDate());
        values.put("mood", mood);
        db.insert("MoodRecord", null, values);
        Toast.makeText(this, "添加成功", Toast.LENGTH_LONG).show();
        db.close();
    }
    public void Help(int state){
        switch (now_state){
            case 0: break;
            case 1:
                setLeft("告诉我你的烦恼吧，也许我可以帮到你。");
                break;
            case 2:
                setLeft("想要尝试缓解心理压力吗？");
                HideInput();
                ShowYesOrNoBtn("尝试一下","下次吧");
                break;
            case 3: setLeft(seq.MoodTalk[4]);HideInput();ShowProblemBtn();break;
            case 4: setLeft(seq.MoodTalk[5]);ShowNothingBtn("是的");break;
            case 5: setLeft(seq.MoodTalk[6]);ShowYesOrNoBtn("改善情绪","尝试放松");break;
            case 6: setLeft(seq.MoodTalk[7]);ShowNothingBtn("好的");break;
            case 7: setLeft(seq.MoodTalk[8]);setLeft(seq.MoodTalk[9]);ShowNothingBtn("好的");break;
            case 8: setLeft(seq.MoodTalk[10]);setLeft(seq.MoodTalk[11]);setLeft(seq.MoodTalk[12]);ShowNothingBtn("放松中");break;
            case 9: setLeft(seq.MoodTalk[13]);ShowInput();now_state=0;break; //Ask=0;
            case 10: setLeft(seq.MoodTalk[14]);setLeft(seq.MoodTalk[15]);setLeft(seq.MoodTalk[16]);ShowNothingBtn("什么事情？");break;
            case 11: setLeft(seq.MoodTalk[17]);setLeft(seq.MoodTalk[18]);ShowNothingBtn("是的");break;
            case 12: setLeft(seq.MoodTalk[19]);setLeft(seq.MoodTalk[20]);ShowNothingBtn("明白");break;
            case 13: setLeft(seq.MoodTalk[21]);setLeft(seq.MoodTalk[22]);ShowNothingBtn("后来呢");break;
            case 14: setLeft(seq.MoodTalk[23]);setLeft(seq.MoodTalk[24]);setLeft(seq.MoodTalk[25]);ShowNothingBtn("但愿如此");break;
            case 15: setLeft(seq.MoodTalk[26]);ShowNothingBtn("谢谢");break;
            case 16: setLeft(seq.MoodTalk[27]);ShowInput();now_state=0;break;
            case 17: setLeft(seq.MoodTalk[28]);setLeft(seq.MoodTalk[29]);setLeft(seq.MoodTalk[30]);ShowNothingBtn("我觉得是这样");break;
            case 18: setLeft(seq.MoodTalk[31]);ShowYesOrNoBtn("重塑思维","认清事实");break;

            case 19: setLeft(seq.MoodTalk[32]);ShowNothingBtn("是的");break;
            case 20: setLeft(seq.MoodTalk[33]); setLeft(seq.MoodTalk[34]);ShowNothingBtn("另一方面呢？");break;
            case 21: setLeft(seq.MoodTalk[35]);ShowNothingBtn("明白");break;
            case 22: setLeft(seq.MoodTalk[36]);ShowNothingBtn("寻找问题的关键");break;
            case 23: setLeft(seq.MoodTalk[37]);ShowYesOrNoBtn("好消息","坏消息");news=0;break;
            case 24: setLeft(seq.MoodTalk[38]);if(news==0) {ShowNothingBtn("那坏消息呢？");news++;}
            else{ShowNothingBtn("该怎么做呢？");news++;} break;
            case 25: setLeft(seq.MoodTalk[39]); if(news==0) {ShowNothingBtn("那好消息呢？");news++;}
            else {ShowNothingBtn("该怎么做呢？");news++;} break;
            case 26: setLeft(seq.MoodTalk[40]);ShowNothingBtn("开始吧");news=0;break;
            case 27: setLeft(seq.MoodTalk[41]); setLeft(seq.MoodTalk[42]); HideBtn(); ShowInput();break;
            case 28: setLeft(seq.MoodTalk[43]); break;
            case 29: setLeft(seq.MoodTalk[44]); setLeft(seq.MoodTalk[45]); break;
            case 30: setLeft(seq.MoodTalk[46]); break;
            case 31: setLeft(seq.MoodTalk[47]);HideInput();ShowYesOrNoBtn("有","没有");break;
            case 32: setLeft(seq.MoodTalk[48]);ShowYesOrNoBtn("有","没有");break;
            case 33: setLeft(seq.MoodTalk[49]);ShowYesOrNoBtn("更糟糕","更好");break;
            case 34: setLeft(seq.MoodTalk[50]); setLeft(seq.MoodTalk[51]); setLeft(seq.MoodTalk[52]);ShowNothingBtn("我懂了");break;
            case 35: setLeft(seq.MoodTalk[53]); HideBtn(); ShowInput();break;
            case 36: setLeft(seq.MoodTalk[54]); break;
            case 37: setLeft(seq.MoodTalk[55]); break;
            case 38: setLeft(seq.MoodTalk[56]); break;
            case 39: setLeft(seq.MoodTalk[57]); setLeft("一开始你说：“"+A+"”，现在你认为“" +B+"，"+C+"，"+D+"，"+E+"。"); setLeft(seq.MoodTalk[59]); setLeft(seq.MoodTalk[60]);
                ShowInput();now_state=0;break;

            case 40:  setLeft(seq.MoodTalk[61]); setLeft(seq.MoodTalk[62]); HideInput();ShowYesOrNoBtn("入眠困难","常有噩梦"); break;
            case 41:  setLeft(seq.MoodTalk[63]); setLeft(seq.MoodTalk[64]); ShowNothingBtn("是的");break;
            case 42:  setLeft(seq.MoodTalk[65]); setLeft(seq.MoodTalk[66]); setLeft(seq.MoodTalk[67]); setLeft(seq.MoodTalk[68]); setLeft(seq.MoodTalk[69]);
                setLeft(seq.MoodTalk[70]); setLeft(seq.MoodTalk[71]); break;
            case 43:  setLeft(seq.MoodTalk[72]);  setLeft(seq.MoodTalk[73]);ShowNothingBtn("真的吗？");break;
            case 44:  setLeft(seq.MoodTalk[74]);  setLeft(seq.MoodTalk[75]);ShowNothingBtn("什么方法？");break;
            case 45:  setLeft(seq.MoodTalk[76]); setLeft(seq.MoodTalk[77]);ShowInput();now_state=0;break;

            case 46:  setLeft(seq.MoodTalk[78]); ShowYesOrNoBtn("尝试缓解","认清事实");break;

            case 47: setLeft(seq.CBT[0]);setLeft(seq.CBT[1]);ShowInput(); break;
            case 48: setLeft(seq.CBT[2]);HideInput();ShowNothingBtn("什么是认知扭曲？");break;
            case 49: setLeft(seq.CBT[3]);setLeft(seq.CBT[4]);setLeft(seq.CBT[5]); ShowYesOrNoBtn("是的","不存在");break;
            case 50: setLeft(seq.CBT[6]);ShowNothingBtn("没错");break;
            case 51: setLeft(seq.CBT[7]);ShowNothingBtn("非黑即白？");break;
            case 52: setLeft(seq.CBT[8]);setLeft(seq.CBT[9]); ShowYesOrNoBtn("是的","不存在");break;
            case 53: setLeft(seq.CBT[10]); now_state=53;
            case 54: setLeft(seq.CBT[11]); now_state=54;ShowYesOrNoBtn("存在","不存在");break;
            case 55: setLeft(seq.CBT[12]); Toast.makeText(this,"!!",Toast.LENGTH_LONG).show();ShowNothingBtn("有趣");break;
            case 56: setLeft(seq.CBT[13]); ShowYesOrNoBtn("是的","并没有");break;
            case 57: setLeft(seq.CBT[14]); setLeft(seq.CBT[15]); ShowNothingBtn("的确");break;
            case 58: setLeft(seq.CBT[16]); ShowNothingBtn("就是这样，没错");break;
            case 59: setLeft(seq.CBT[17]); ShowNothingBtn("谢谢~");break;
            case 60: setLeft(seq.CBT[18]); setLeft("你原先的想法是："+A); ShowInput(); break;
            case 61: setLeft(seq.CBT[19]); HideInput();ShowYesOrNoBtn("好多了","不知道该怎么办");break;
            case 62: setLeft(seq.CBT[20]); ShowNothingBtn("比如说？");break;
            case 63: setLeft(seq.CBT[21]); setLeft(seq.CBT[22]);ShowNothingBtn("大概懂了"); break;
            case 64: setLeft(seq.CBT[23]); now_state=0;ShowInput();HideBtn();break;


            case 65: setLeft(seq.CTF[0]); setLeft(seq.CTF[1]); setLeft(seq.CTF[2]); setLeft(seq.CTF[3]); ShowNothingBtn("我懂了");break;
            case 66: setLeft(seq.CTF[4]); setLeft(seq.CTF[5]); ShowNothingBtn("现在就开始吧");break;
            case 67: setLeft(seq.CTF[6]); setLeft(seq.CTF[7]); ShowNothingBtn("真是糟糕");break;
            case 68: setLeft(seq.CTF[8]); setLeft(seq.CTF[9]);setLeft(seq.CTF[10]); ShowNothingBtn("事实却可能不是这样的");break;
            case 69: setLeft(seq.CTF[11]); ShowInput(); break;
            case 70: setLeft(seq.CTF[12]);setLeft(seq.CTF[13]);setLeft(seq.CTF[14]);setLeft(seq.CTF[15]);setLeft(seq.CTF[16]);HideInput();ShowNothingBtn("哇");break;
            case 71: setLeft(seq.CTF[17]); ShowNothingBtn("没错");break;
            case 72: setLeft(seq.CTF[18]);setLeft(seq.CTF[19]);setLeft(seq.CTF[20]); ShowInput(); break;
            case 73: setLeft(seq.CTF[21]); break;
            case 74: setLeft("接下来我们要列出所有"+B+"发展中存在的潜在可能性。"); break;
            case 75: setLeft("现在我希望你能更客观的描述这个造成你"+A+"的事情……意思是，从你眼睛、鼻子、耳朵中直接得到的信息。");setLeft(seq.CTF[24]); break;
            case 76: setLeft(seq.CTF[25]);setLeft(seq.CTF[26]); now_state=0;break;
        }
    }


}
