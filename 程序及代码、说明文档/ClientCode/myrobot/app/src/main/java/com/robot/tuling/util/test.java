package com.robot.tuling.util;

import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Matrix;
import android.net.Uri;
import android.os.Environment;
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
import com.robot.tuling.constant.Classifier;

import org.opencv.android.OpenCVLoader;
import org.opencv.android.Utils;
import org.opencv.core.Mat;
import org.opencv.core.MatOfRect;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.objdetect.CascadeClassifier;
import org.opencv.core.Rect;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.*;


public class test extends AppCompatActivity {

    static{

        //   System.loadLibrary("native-lib");

        if(!OpenCVLoader.initDebug()){
            Log.d("opencv", "初始化失败");
        }else
            Log.d("opencv", "初始化成功 ");
    }

    private String TAG = "Faceactivity";
    private ImageView imageView;
    private TextView reslutTextView;
    private Button getPhotoButton, greyPhotoButton,getPhotoFromAlbum;
    private Classifier classifier;//识别类
    private static final String MODEL_FILE = "file:///android_asset/tensor_model.pb";
    private static final int IMAGE_SIZE = 48;
    private Uri imageUri=null;
    private Bitmap bitmap,bitmap2=null;
    private ArrayList<Bitmap> bitmaps=null;
    private Rect[] facesArray=null;
    private int bitlenth = 0;
    private String pathString= null;
    public static final int TAKE_PHOTO = 1;
    private CascadeClassifier cascadeClassifier = null; //级联分类器
    private int absoluteFaceSize = 0;
    private int flag = 0;



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


    //缩放图片,使用openCV，缩放方法采用area interpolation法
    private Bitmap scaleImage(Bitmap bitmap, int width, int height)
    {

        Mat src = new Mat();
        Mat dst = new Mat();
        Utils.bitmapToMat(bitmap, src);
        Imgproc.resize(src, dst, new Size(width,height),0,0,Imgproc.INTER_AREA);
        Bitmap bitmap1 = Bitmap.createBitmap(dst.cols(),dst.rows(),Bitmap.Config.ARGB_8888);
        Utils.matToBitmap(dst, bitmap1);
        return bitmap1;
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

    Bitmap adjustPhotoRotation(Bitmap bm, final int orientationDegree)
    {
        Matrix m = new Matrix();
        m.setRotate(orientationDegree, (float) bm.getWidth() / 2, (float) bm.getHeight() / 2);

        try {
            Bitmap bm1 = Bitmap.createBitmap(bm, 0, 0, bm.getWidth(), bm.getHeight(), m, true);
            return bm1;
        } catch (OutOfMemoryError ex) {
        }
        return null;

    }

    private ArrayList<Bitmap> detectFaceAndOp(Bitmap bitmap)
    {

        Mat img = new Mat();
        Utils.bitmapToMat(bitmap, img);

        Mat imgGray = new Mat();;
        MatOfRect faces = new MatOfRect();

        if(img.empty())
        {
            Log.d("ccx","detectFace but img is empty");
            return null;
        }

        if(img.channels() ==3)
        {
            Imgproc.cvtColor(img, imgGray, Imgproc.COLOR_RGB2GRAY);
        }
        else
        {
            imgGray = img;
        }

        cascadeClassifier.detectMultiScale(imgGray, faces, 1.1, 2, 2, new Size(absoluteFaceSize, absoluteFaceSize), new Size());

        facesArray = faces.toArray();
        bitlenth = facesArray.length;
        ArrayList<Bitmap> bits = new ArrayList<Bitmap>();
        Log.d("bitlenth", " "+bitlenth);
        if (facesArray.length > 0){
            for (int i = 0; i < bitlenth; i++) {
                Imgproc.rectangle(imgGray, facesArray[i].tl(), facesArray[i].br(), new Scalar(0,255, 0, 255), 3);
                Utils.matToBitmap(imgGray, bitmap);
                Bitmap destBitmap = Bitmap.createBitmap(bitmap, (int) (facesArray[i].tl().x), (int) (facesArray[i].tl().y), facesArray[i].width, facesArray[i].height);
                Bitmap scaleImage = scaleImage(destBitmap, 48, 48);
                bits.add(toGrayscale(scaleImage));
                Log.d("ccx","index:" + i + "topLeft:" + facesArray[i].tl() + "bottomRight:" + facesArray[i].br()+ "height:" + facesArray[i].height);
            }
        }
        else{
            Log.d("ccx", "detectFaceAndOp: 未探测到人脸");
            return null;
        }

        return bits;
    }

    private void face_recogn(ArrayList<Bitmap> bits){
        Bitmap newbitmap = null;
        //0=Angry, 1=Disgust, 2=Fear, 3=Happy, 4=Sad, 5=Surprise, 6=Neutral
        for(int i=0; i<bitlenth; i++) {
            String str = String.valueOf(classifier.getPredict(getSingleChannelPixel(bits.get(i))));
            switch (str) {
                case "0":
                    str = "生气";
                    break;
                case "1":
                    str = "厌恶";
                    break;
                case "2":
                    str = "恐惧";
                    break;
                case "3":
                    str = "开心";
                    break;
                case "5":
                    str = "难过";
                    break;
                case "6":
                    str = "惊讶";
                    break;
                case "4":
                    str = "平静";
                    break;
                default:
                    Log.d("ccx", "Tensorflow return is error.");
                    break;
            }

            android.graphics.Bitmap.Config bitmapConfig = bitmap.getConfig();
            newbitmap = bitmap.copy(bitmapConfig,true);
            Canvas canvas = new Canvas(newbitmap);
            Paint textpaint = new Paint(); //创建画笔
            textpaint.setColor(Color.RED);//设置颜色
            textpaint.setStyle(Paint.Style.FILL);//设置样式
            textpaint.setTextSize(90);
            canvas.drawText(str,(float) (((facesArray[i].br().x)+(facesArray[i].tl().x))/2),(float) ((facesArray[i].br().y)),textpaint);
            bitmap = newbitmap;

        }
        imageView.setImageBitmap(bitmap);
    }

    private void initializeOpenCVDependencies() {
        try {
            InputStream is = getResources().openRawResource(R.raw.haarcascade_frontalface_alt);
            File cascadeDir = getDir("cascade", Context.MODE_PRIVATE);
            File mCascadeFile = new File(cascadeDir, "haarcascade_frontalface_alt.xml");
            FileOutputStream os = new FileOutputStream(mCascadeFile);
            byte[] buffer = new byte[4096];
            int bytesRead;
            while ((bytesRead = is.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
            }
            is.close();
            os.close();
            // 加载cascadeClassifier
            cascadeClassifier = new CascadeClassifier(mCascadeFile.getAbsolutePath());
        } catch (Exception e) {
            Log.e("opencv","Error loading cascade");
        }
    }

    private  void openCa(){
        String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        pathString = Environment.getExternalStorageDirectory()+ "/tempImage" +timestamp+ ".jpg";
        Log.d(TAG, "openCa:这里是pathstring： "+pathString);
        File outputImage = new File(Environment.getExternalStorageDirectory(),
                "tempImage"+timestamp+ ".jpg");
        Log.d(TAG, "rempImage: "+outputImage);

      //  imageUri = FileProvider.getUriForFile(FaceActivity.this,
     //           BuildConfig.APPLICATION_ID + ".provider",
      //          outputImage); //得到存储地址的uri
        Log.d(TAG, "openCa的imageUri: "+imageUri);
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);//进行拍照
        intent.putExtra(MediaStore.EXTRA_OUTPUT, imageUri);//指定图片的输出地址
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
                Log.d(TAG, "onactivity中的imageUri: "+imageUri);
                imgPath = pathString; //取得拍照存储地址
                Log.d(TAG, "onactivity中的imgpath: "+imgPath);
            }

            if (requestCode == 1) {
                //解析得到所选相册图片的地址
                Uri selectImg = data.getData();
                String[] filePathColumn = {MediaStore.Images.Media.DATA};
            //    Cursor cursor = FaceActivity.this.getContentResolver().query(selectImg,filePathColumn,null,null,null);
          //      cursor.moveToFirst();
           //     int columnIndex = cursor.getColumnIndex(filePathColumn[0]);
            //    imgPath = cursor.getString(columnIndex);
           //     cursor.close();
            }

            bitmap = BitmapFactory.decodeFile(imgPath);
            Log.d(TAG, "bitmap: "+bitmap);
            imageView.setImageBitmap(bitmap);
            bitmaps = detectFaceAndOp(bitmap);

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
                    if(bitmaps == null){
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

                    break;
                default:
                    break;
            }
        }

    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        classifier = new Classifier(getAssets(),MODEL_FILE);
        setContentView(R.layout.activity_face);
        imageView = (ImageView)findViewById(R.id.img_ccx);
        getPhotoButton = (Button)findViewById(R.id.btn_get_photo);
        greyPhotoButton = (Button)findViewById(R.id.btn_grey_photo);
        getPhotoFromAlbum = (Button)findViewById(R.id.btn_get_photo_from_album);
        initializeOpenCVDependencies();
        getPhotoButton.setOnClickListener(new MyClickListener());
        getPhotoFromAlbum.setOnClickListener(new MyClickListener());
        greyPhotoButton.setOnClickListener(new MyClickListener());
    }




}
