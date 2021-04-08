package com.robot.tuling.ui;

import android.content.ContentValues;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Path;
import android.media.FaceDetector;
import android.media.Image;
import android.net.Uri;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.provider.MediaStore;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import com.robot.tuling.BuildConfig;
import com.robot.tuling.R;
import com.robot.tuling.adapter.ImageUpload;
import com.robot.tuling.constant.Classifier;
import com.robot.tuling.constant.DataBase;


import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.text.SimpleDateFormat;
import java.util.*;

import cn.pedant.SweetAlert.SweetAlertDialog;


public class FaceActivity extends AppCompatActivity {


    private String imagePath;
    private String TAG = "Faceactivity";
    private ImageView imageView;
    private TextView reslutTextView;
    private Button getPhotoButton, greyPhotoButton,getPhotoFromAlbum;
    private static final int IMAGE_SIZE = 48;
    private Uri imageUri=null;
    private Bitmap bitmap,bitmap2=null;
    private ArrayList<Bitmap> bitmaps=null;
    private int bitlenth = 0;
    private String pathString= null;
    public static final int TAKE_PHOTO = 1;
    private int absoluteFaceSize = 0;
    private int flag = 0;
    private TextView resultShow ;
    private Context mcontext;
    private SweetAlertDialog pDialog;
    private TextView emoji_result;
    private File f;
    private String IP = "192.168.1.5";
    private int PORT = 6668;
    private String url = "http://192.168.1.5:5000/upload";
    public static Bitmap toGrayscale(Bitmap bmpOriginal) {
        int width, height;
        height = bmpOriginal.getHeight();
        width = bmpOriginal.getWidth();

        Bitmap bmpGrayscale = Bitmap.createBitmap(width, height, Bitmap.Config.RGB_565);
        Canvas c = new Canvas(bmpGrayscale);
        Paint paint = new Paint();
        ColorMatrix cm = new ColorMatrix();
        cm.setSaturation(0);
        ColorMatrixColorFilter f = new ColorMatrixColorFilter(cm);
        paint.setColorFilter(f);
        c.drawBitmap(bmpOriginal, 0, 0, paint);
        return bmpGrayscale;
    }
    private String getURL(){
        DataBase dbHelper = new DataBase(this, "ip.db", null, 1);
        SQLiteDatabase db = dbHelper.getReadableDatabase();// 打开数据库
        String sql = "select * from UserMessage";
        Cursor cursor = db.rawQuery(sql, null);
        while (cursor.moveToNext()) {
            IP = cursor.getString(0);
            break;
        }
        url = "http://"+IP+":5000/upload";
        return url;
    }

    //获取输入像素集
    public float[] getSingleChannelPixel(Bitmap bitmap) {
        float[] floatValues = new float[IMAGE_SIZE * IMAGE_SIZE * 1];

        if ((bitmap.getWidth() != IMAGE_SIZE) ||  (bitmap.getHeight() != IMAGE_SIZE)){
            Log.d("getSingleChannelPixel","获取像素时图片尺寸不对");
        }

        StringBuffer sBuffer = new StringBuffer("像素值：");
        for(int i = 0;i<bitmap.getWidth();i++)
        {
            for(int j =0;j<bitmap.getHeight();j++)
            {
                int col = bitmap.getPixel(i, j);
                int alpha = col&0xFF000000;
                int red = (col&0x00FF0000)>>16;
                int green = (col&0x0000FF00)>>8;
                int blue = (col&0x000000FF);
                int gray = (int)((float)red*0.3+(float)green*0.59+(float)blue*0.11);
                //int newColor = alpha|(gray<<16)|(gray<<8)|gray;
                floatValues[i + j* IMAGE_SIZE] = gray;
                sBuffer.append(gray) ;
                sBuffer.append(" ") ;
            }
        }
        return floatValues;
    }



    private void face_recogn(ArrayList<Bitmap> bits){

    }

/*
    private  void openCa(){
        String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        pathString = Environment.getExternalStorageDirectory()+ "/tempImage" +timestamp+ ".jpg";
        Log.d(TAG, "openCa:这里是pathstring： "+pathString);
        File outputImage = new File(Environment.getExternalStorageDirectory(),
                "tempImage"+timestamp+ ".jpg");
        Log.d(TAG, "rempImage: "+outputImage);

        //imageUri = FileProvider.getUriForFile(FaceActivity.this,
        //        BuildConfig.APPLICATION_ID+ ".provider",
        //        outputImage); //得到存储地址的uri
        //Log.d(TAG, "openCa的imageUri: "+imageUri);
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);//进行拍照
        //intent.putExtra(MediaStore.EXTRA_OUTPUT, imageUri);//指定图片的输出地址
        startActivityForResult(intent, 0);
    }
*/

    private void openCa(){
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(intent, 0);
    }
    private void selectImage(){
        Intent intent = new Intent(Intent.ACTION_PICK,MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(intent,1);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if((requestCode==0 || requestCode==1 )&&resultCode==RESULT_OK) {
            String imgPath = null;
            if (requestCode == 0) {
                //Log.d(TAG, "onactivity中的imageUri: "+imageUri);
               // imgPath = pathString; //取得拍照存储地址
               // Log.d(TAG, "onactivity中的imgpath: "+imgPath);


                String sdStatus = Environment.getExternalStorageState();
                if (!sdStatus.equals(Environment.MEDIA_MOUNTED)) { // 检测sd是否可用
                    Log.v("TestFile", "SD card is not avaiable/writeable right now.");
                    return;
                }

                Bundle bundle = data.getExtras();
                Bitmap bitmap = (Bitmap) bundle.get("data");// 获取相机返回的数据，并转换为Bitmap图片格式
                FileOutputStream b = null;
                File file = new File("/sdcard/myImage/");
                file.mkdirs();// 创建文件夹，名称为myimage

                //照片的命名，目标文件夹下，以当前时间数字串为名称，即可确保每张照片名称不相同。网上流传的其他Demo这里的照片名称都写死了，则会发生无论拍照多少张，后一张总会把前一张照片覆盖。细心的同学还可以设置这个字符串，比如加上“ＩＭＧ”字样等；

                String str=null;
                Date date=null;
                SimpleDateFormat format = new SimpleDateFormat("yyyyMMddHHmmss");//获取当前时间，进一步转化为字符串
                date =new Date();
                str=format.format(date);
                String fileName = "/sdcard/myImage/"+str+".jpg";
                imgPath = fileName;
                try {
                    b = new FileOutputStream(fileName);
                    bitmap.compress(Bitmap.CompressFormat.JPEG, 100, b);// 把数据写入文件
                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                } finally {
                    try {
                        b.flush();
                        b.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }

            if (requestCode == 1) {
                //解析得到所选相册图片的地址
                Uri selectImg = data.getData();
                String[] filePathColumn = {MediaStore.Images.Media.DATA};
                Cursor cursor = FaceActivity.this.getContentResolver().query(selectImg,filePathColumn,null,null,null);
                cursor.moveToFirst();
                int columnIndex = cursor.getColumnIndex(filePathColumn[0]);
                imgPath = cursor.getString(columnIndex);
                cursor.close();
            }

            imagePath = imgPath;
            bitmap = BitmapFactory.decodeFile(imgPath);
            Log.d(TAG, "bitmap: "+bitmap);
            imageView.setImageBitmap(bitmap);

        }
    }


    class MyClickListener implements View.OnClickListener {
        @Override
        public void onClick(View v) {
            // TODO Auto-generated method stub
            switch (v.getId()) {
                case R.id.btn_get_photo:
                    openCa();
                    flag = 1;
                    break;
                case R.id.btn_get_photo_from_album:
                    selectImage();
                    flag = 2;
                    break;
                case R.id.btn_grey_photo:
                    if(imagePath==null){
                        ShowErrorDialog("😉请先选择一张图片哦");
                        break;
                    }
                    ShowLoadingDialog("Loading 😘");
                    SendOkHttp(v);
                    //SendSocket(v);
                    break;
                    /*if(bitmaps == null){
                        if(flag == 1) {
                            Toast.makeText(getApplicationContext(),"未检测到人脸，请重新拍摄",Toast.LENGTH_LONG).show();
                            openCa();
                        }
                        if (flag == 2) {
                            Toast.makeText(getApplicationContext(),"未检测到人脸，请重新选取图像",Toast.LENGTH_LONG).show();
                            selectImage();
                        }
                    }
                    else
                        try {
                            face_recogn(bitmaps);
                        }catch (Exception e){
                            e.printStackTrace();
                        }

                    break;*/
                default:
                    break;
            }
        }

    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_face);
        imagePath = null;
        mcontext = this;
        imageView = (ImageView)findViewById(R.id.img_ccx);
        getPhotoButton = (Button)findViewById(R.id.btn_get_photo);
        greyPhotoButton = (Button)findViewById(R.id.btn_grey_photo);
        getPhotoFromAlbum = (Button)findViewById(R.id.btn_get_photo_from_album);
        resultShow = (TextView)findViewById(R.id.result);
        getPhotoButton.setOnClickListener(new MyClickListener());
        getPhotoFromAlbum.setOnClickListener(new MyClickListener());
        greyPhotoButton.setOnClickListener(new MyClickListener());
        emoji_result = (TextView)findViewById(R.id.emoji_result);
        pDialog = new SweetAlertDialog(this, SweetAlertDialog.PROGRESS_TYPE);

    }


    private Handler handler = new Handler() {
        @Override
        public void handleMessage(Message msg) {
            super.handleMessage(msg);
            switch (msg.what) {
                case 1:
                    //Toast.makeText(mcontext,msg.obj.toString(),Toast.LENGTH_LONG).show();
                    if(msg.obj.toString().contains("空")){
                        emoji_result.setText("啊哦，没有识别到人脸👩");
                        ShowErrorDialog("没有识别到👩");
                        break;
                    }
                    ShowSuccessDialog(emojiChange(msg.obj.toString()));
                    emoji_result.setText(msg.obj.toString());
                    String new_alr = ChangeMood(msg.obj.toString());
                    InsertMood(new_alr);
                    break;
                case 2:
                    ShowErrorDialog("网络连接失败！");
                    break;
            }
        }

    };

    public String ChangeMood(String cur){
        switch (cur){
            case "喜悦":
                return "开心";
            case "悲伤":
                return "难过";
            case "愤怒":
                return "生气";
            case "平静":
                return "平静";
            default:
                return "难过";
        }
    }
    public String getMyDate(){
        SimpleDateFormat simpleDateFormat = new SimpleDateFormat("yyyy年MM月dd日");// HH:mm:ss
//获取当前时间
        Date date = new Date(System.currentTimeMillis());
        return simpleDateFormat.format(date);
    }

    public void InsertMood(String cur) {
        DataBase dbHelper = new DataBase(this, "Chatbot.db", null, 1);
        SQLiteDatabase sqLiteDatabase = dbHelper.getWritableDatabase();
        //ContentValues values = new ContentValues();
        //values.put("mood",cur);

        String sql = "update MoodRecord set mood = '"+cur+"' where date='"+getMyDate()+"'";
        //String[] args = {String.valueOf(getMyDate())};
        //sqLiteDatabase.update("MoodRecord",values,"date=?",args);
        //sqLiteDatabase.close();
        sqLiteDatabase.execSQL(sql);

        Toast.makeText(this,"今日心情更新成功!"+getMyDate()+"?",Toast.LENGTH_SHORT).show();
    }

    public void SendSocket(View view) {
        new Thread() {
            @Override
            public void run() {
                try {
                    //Socket sed_socket = new Socket("192.168.1.5", 6668);
                    Socket sed_socket = new Socket();
                    SocketAddress socAddress = new InetSocketAddress(IP, PORT);
                    sed_socket.connect(socAddress, 5000);
                    boolean connected = sed_socket.isConnected();
                    Log.i("连接","连接？" + connected);

                    DataOutputStream out = new DataOutputStream(sed_socket.getOutputStream());

                    FileInputStream fis = new FileInputStream(imagePath);
                    //发送图片大小
                    int size = fis.available();
                    String s = String.valueOf(size);
                    while(s.length()<10){
                        s = s + " ";
                    }
                    byte[] bytes = s.getBytes();
                    out.write(bytes);
                    out.flush();
                    //发送图片
                    //读取图片到ByteArrayOutputStream
                    byte[] sendBytes = new byte[1024];
                    int length = 0;
                    while ((length = fis.read(sendBytes, 0, sendBytes.length)) > 0) {
                        out.write(sendBytes, 0, length);
                        out.flush();
                    }
                    fis.close();

//                    Socket rev_socket = new Socket("192.168.1.5", 6668);
                    Log.i("连接","上");
                    try {
                        BufferedReader in = new BufferedReader(new InputStreamReader(sed_socket.getInputStream(), "UTF-8"));
                        String emotion = in.readLine();

                        Message message = handler.obtainMessage();
                        message.what = 1;
                        message.obj = emotion;
                        handler.sendMessage(message);

                        Log.i("连接", emotion);
                        in.close();
                        Log.i("连接", "下");
                    }catch (IOException e){
                        Log.i("连接", "读取失败");
                        Log.i("连接", e.getMessage().toString());
                    }


                } catch (IOException e) {
                    Log.i("连接", "失败");
                    e.printStackTrace();
                    Log.i("连接", e.getMessage().toString());
                    Message message = handler.obtainMessage();
                    message.what = 2;
                    handler.sendMessage(message);
                }
            }
        }.start();
    }


    public void ShowLoadingDialog(String msg){
        pDialog = new SweetAlertDialog(this, SweetAlertDialog.PROGRESS_TYPE);
        pDialog.getProgressHelper().setBarColor(Color.parseColor("#A5DC86"));
        pDialog.setTitleText(msg);
        pDialog.setCancelable(false);
        pDialog.show();

    }

    public void ShowErrorDialog(String msg){
        pDialog.changeAlertType(SweetAlertDialog.ERROR_TYPE);
        pDialog.setTitleText("Oops...");
        pDialog.setContentText(msg);
        pDialog.show();
    }
    public void ShowSuccessDialog(String mood){
        pDialog.changeAlertType(SweetAlertDialog.SUCCESS_TYPE);
        pDialog.setTitleText("Success");
        pDialog.setContentText(mood);
    }
    public void HideLoadingDialog(){
        pDialog.hide();
    }
    //imgaePath
    public void SendOkHttp(View view) {
        new Thread() {
            @Override
            public void run() {
                f = new File(imagePath);
                try {
                    //上传图片
                    url = getURL();
                    ImageUpload.run(f,url);
                    while(true){
                        if(ImageUpload.getAnswer() == "无")
                            continue;
                        break;
                    }
                    Message message = handler.obtainMessage();
                    message.what = 1;
                    String x = ImageUpload.getAnswer();
                    if (x == "未连接" || x =="失败")
                        message.what = 2;
                    else
                        message.what = 1;
                        message.obj = x;
                    handler.sendMessage(message);
                    ImageUpload.ChangeAnswer();
                } catch (Exception e) {
                    e.printStackTrace();
                    Message message = handler.obtainMessage();
                    message.what = 2;
                    handler.sendMessage(message);
                }
            }
        }.start();
    }
    public String emojiChange(String x){
        switch (x){
            case "喜悦":
                return "😊看来你今天心情很好呢";
            case "悲伤":
                return "不开心了吗，摸摸头☹";
            case "愤怒":
                return "生气了哦？不气不气";
            case "恐惧":
                return "可以告诉我你在害怕什么吗";
            case "惊讶":
                return "哦？有什么惊奇的事情么";
            case "平静":
                return "太阳当空照，花儿对你笑🌸";
            case "厌恶":
                return "遇到什么讨厌的事情了吗？";
            default:break;

        }
        return "请重新选择";
    }
}
