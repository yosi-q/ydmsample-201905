# セットアップ内容

- DynamoDBに以下の内容のテーブルを作成
  - テーブル名: yesno_result
  - テーブル項目:
    - click_type: String ... IoTボタンのアクションを記録 (SINGLE/DOUBLE/LONG)
    - reported_time: String ... IoTボタンのアクション時間を記録 (2019-12-08T12:34:56.789Z)