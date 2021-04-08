package com.robot.tuling.adapter;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.os.Handler;
import android.os.Message;
import android.widget.Toast;

import com.robot.tuling.constant.DataBase;
import com.robot.tuling.ui.MainActivity;

import java.io.File;
import java.io.IOException;
import java.util.UUID;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class ImageUpload{

    /**
     * The imgur client ID for OkHttp recipes. If you're using imgur for anything other than running
     * these examples, please request your own client ID! https://api.imgur.com/oauth2
     */
    private static final String IMGUR_CLIENT_ID = "123";
    private static final MediaType MEDIA_TYPE_PNG = MediaType.parse("image/png");

    private static final OkHttpClient client = new OkHttpClient();
    private static String answer = "无";
   // private static String url = "http://192.168.1.5:5000/upload";
    public static void run(File f, String url) throws Exception {
        final File file=f;
        new Thread() {
            @Override
            public void run() {
                //子线程需要做的工作
                RequestBody requestBody = new MultipartBody.Builder()
                        .setType(MultipartBody.FORM)
                        .addFormDataPart("title", "Square Logo")
                        .addFormDataPart("file", UUID.randomUUID().toString()+".png",
                                RequestBody.create(MEDIA_TYPE_PNG, file))
                        .build();
                //设置为自己的ip地址
                Request request = new Request.Builder()
                        .header("Authorization", "Client-ID " + IMGUR_CLIENT_ID)
                        .url(url)
                        .post(requestBody)
                        .build();

                /*try (Response response = client.newCall(request).execute()) {
                    if (!response.isSuccessful()) throw new IOException("Unexpected code " + response);

                    System.out.println(response.body().string());
                    answer = response.body().string();
                   // answer = response.body().string(); //结果

                } catch (IOException e) {
                    e.printStackTrace();
                }*/

                Call call = client.newCall(request);
                call.enqueue(new Callback() {
                    @Override
                    public void onFailure(Call call, IOException e) {
                            //Toast.makeText(MainActivity.this, "服务器错误", Toast.LENGTH_SHORT).show();
                        answer = "未连接";
                    }

                    @Override
                    public void onResponse(Call call, final Response response) throws IOException {
                        final String res = response.body().string();
                        if (res.equals("0")) {
                            //Toast.makeText(MainActivity.this, "失败", Toast.LENGTH_SHORT).show();
                           answer = "失败";
                        } else {
                            //Toast.makeText(MainActivity.this, "成功"+res, Toast.LENGTH_SHORT).show();
                            answer = res;

                        }
                    }
                });

            }
        }.start();
    }
    public static String getAnswer(){
        return answer;
    }
    public static void ChangeAnswer(){
        answer = "无";
    }
}
