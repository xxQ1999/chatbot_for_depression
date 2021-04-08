package com.robot.tuling.util;

import android.graphics.Color;
import android.text.Spannable;
import android.text.SpannableString;
import android.text.style.ForegroundColorSpan;

import java.util.ArrayList;
import java.util.List;

public class SpecialViewUtil {

    public static SpannableString getSpannableStringByTagItem(String text, String tagItem, int count) {
        if (count <= 0) return null;
        List<String> list = new ArrayList<>();
        for (int i=0; i<count; i++) {
            list.add(tagItem);
        }
        return getSpannableString(text, list);
    }

    public static SpannableString getSpannableString(String text, List<String> tagList) {
        int lastIndex = -1;
        SpannableString spannableString = new SpannableString(text);
        for (int i = 0; i < tagList.size(); i++) {
            int index = text.indexOf(tagList.get(i), lastIndex);
            if (index != lastIndex) {
                lastIndex = index+tagList.get(i).length();
                spannableString.setSpan(new ForegroundColorSpan(Color.parseColor("#00897b")),
                        index, index+tagList.get(i).length(), Spannable.SPAN_INCLUSIVE_INCLUSIVE);
            }
        }
        return spannableString;
    }

    /**
     *  SpannableString颜色为橙色
     */
    public static SpannableString getSpannableString(String text, String tag) {
        SpannableString spannableString = new SpannableString(text);
        int index = text.indexOf(tag);
        if (index != -1) {
            spannableString.setSpan(new ForegroundColorSpan(Color.parseColor("#00897b")),
                    index, index + tag.length(), Spannable.SPAN_INCLUSIVE_INCLUSIVE);
        }
        return spannableString;
    }

}
