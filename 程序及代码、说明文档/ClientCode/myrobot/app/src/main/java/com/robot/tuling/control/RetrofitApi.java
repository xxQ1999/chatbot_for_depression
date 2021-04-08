package com.robot.tuling.control;

import com.robot.tuling.entity.MessageEntity;

import io.reactivex.Observable;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Query;


public interface RetrofitApi {

    // 请求图灵API接口，获得问答信息
    @GET("api")
    Call<MessageEntity> getTuringInfo(@Query("key") String key, @Query("info") String info);

    // 请求图灵API接口，获得问答信息
    @GET("api")
    Observable<MessageEntity> getTuringInfoByRxJava(@Query("key") String key, @Query("info") String info);

    Observable<MessageEntity> getJokeInfoByRxJava(@Query("key") String key);
}
