package com.robot.tuling.sharedpreferences;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.SharedPreferences;
import android.os.Build;

public class SettingsSharedPreferences$$Impl
    implements SettingsSharedPreferences, de.devland.esperandro.SharedPreferenceActions {

  private final SharedPreferences preferences;

  public SettingsSharedPreferences$$Impl(Context context) {
    this.preferences = context.getSharedPreferences("settings", Context.MODE_PRIVATE);
  }

  @Override
  public boolean isReceivePush() {
    return preferences.getBoolean("isReceivePush", false);
  }

  @Override
  @SuppressLint({"NewApi", "CommitPrefEdits"})
  public void isReceivePush(boolean isReceivePush) {
    preferences.edit().putBoolean("isReceivePush", isReceivePush).apply();
  }

  @Override
  public SharedPreferences get() {
    return preferences;
  }

  @Override
  public boolean contains(String key) {
    return preferences.contains(key);
  }

  @Override
  @SuppressLint({"NewApi", "CommitPrefEdits"})
  public void remove(String key) {
    preferences.edit().remove(key).apply();
  }

  @Override
  public void registerOnChangeListener(android.content.SharedPreferences.OnSharedPreferenceChangeListener listener) {
    preferences.registerOnSharedPreferenceChangeListener(listener);
  }

  @Override
  public void unregisterOnChangeListener(android.content.SharedPreferences.OnSharedPreferenceChangeListener listener) {
    preferences.unregisterOnSharedPreferenceChangeListener(listener);
  }

  @Override
  @SuppressLint({"NewApi", "CommitPrefEdits"})
  public void clear() {
    preferences.edit().clear().apply();
  }

  @Override
  @SuppressLint({"NewApi", "CommitPrefEdits"})
  public void clearDefined() {
    SharedPreferences.Editor editor = preferences.edit();
    editor.remove("isReceivePush");
    editor.apply();
  }

  @Override
  public void initDefaults() {
    this.isReceivePush(this.isReceivePush());
  }

}
