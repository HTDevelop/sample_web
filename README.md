OpenTelemetryに対してトレース、メトリクス、ログを送るサンプルです。

### 実行方法
## 前提
* Linux環境での実行を想定しています。
* Python3.13がインストールされている前提 or Dockerがインストールされている前提です。
* AWS認証情報は~/.aws/credentialsに記載するか、環境変数に設定されている前提です。
## 手順（共通）
1. app/utils/observability.pyのself.__endpointの欄を自信のOpenTelemetryのエンドポイントに変更
※NLBのURLになっていますが、OpenTelemetryにアクセスできればなんでもよいです。

## 手順（Python）
1. flask立ち上げ
```
cd app
python app.py
```
2. ポート80にアクセス（http://localhost:80）

## 手順（Docker）
1. ビルド＆実行
```
docker build . -t sample_web:latest
docker run 80:80 -e AWS_REGION=ap-northeast-1 -e AWS_ACCESS_KEY_ID=XXXXXXXXXXXX -e AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXX sample_web:latest
```
2. ポート80にアクセス（http://localhost:80）
