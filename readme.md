# るしぼっと うぃん　～取扱説明書 兼 設計仕様書～
::ProjectName= Lucibot Win (master)
::github= https://github.com/lucida3rd/lucibot_win
::Admin= Lucida（lucida3hai@twitter.com）
::TwitterURL= https://twitter.com/lucida3hai

::Update= 2020/10/27
::Version= 1.0.0.0


<a id="iSystemSummary"></a>
## システム概要
python3で作成したWindows環境下で動くことを前提にしたTwitter支援用botです。
・指定のワードを入力し、直近でワードをツイートしているユーザを検出、CSVに出力します。
・指定した期間、リフォローを貰えなかったユーザをアンフォローします。
・一度フォローされたけどアンフォローされたユーザをアンフォローします。
・なお、botでアンフォローしたユーザは指定のリストに追加され、次回の抽出から除外されます。
・指定した期間を過ぎたいいねを解除します。いいねリストをクリーンにします。




<a id="iRet"></a>
## 目次
* [システム概要](#iSystemSummary)
* [前提](#iPremise)
* [githubアカウントの取り方](#iGetGithub)
* [Twitterリストの作成](#iGetTwitterList)
* [デフォルトエンコードの確認](#iDefEncode)
* [Twitter APIの取得方法](#iGetTwitter)
* [セットアップ手順](#iSetup)
* [アップデート手順](#iUpdate)
* [起動方法](#iStart)
* [免責事項](#iDisclaimer)
* [謝辞](#iAcknowledgment)




<a id="iPremise"></a>
## 前提
* python3（v3.8.5で確認）
* postgreSQL（Windows版）
* Windows 10
* twitterアカウント
* twitterリスト: normal
* twitterリスト: un_refollow
* githubアカウント
* デフォルトエンコード：utf-8

> **補足1**
> * githubアカウントがなくても運用にこぎつけることはできますが、バージョン管理できないのでここではgithub垢持ってる前提で記載します。
> * 以上の前提が異なると一部機能が誤動作の可能性があります。

> **補足2**
> 本アプリはLucibot4ベースですが、今回はWindows 10で開発しているため、Linux系では誤動作をおこすかもしれません。
> おそらくは問題ないと思いますがご留意ください。

> **Twitterの審査について**
> Twitter APIを利用するにあたって、審査を受ける必要があります。審査に通らないと本ソフトは利用できません。
> この審査は大学などの論文発表の場と考えてください。
> 申請の入力方法については以後に記載しますが、恐らく同じことを何度も聞かれると思います。
> しかし、どうか諦めず根気よく回答してください。そうすることで回答すると審査が通りやすくなります。
> 審査のコツ：
> * ビジネス利用でないことを説明する。
> * このソフトでできること、処理の方法や方式、出力結果を"細かく"説明する。
> * 根気よく、なるべく諦めない。
> * どうしても分からない場合は"わかんないものは分からん！"と素直に答える。




<a id="iGetGithub"></a>
## githubアカウントの取り方
おそらくこのドキュメントを見られてる方はgithubアカウントをお持ちと思いますが念のため。
githubのホームページから取得できます。
　　[github.com](https://github.com)



<a id="iGetTwitterList"></a>
## Twitterリストの作成　★初回のみ
フォロワー監視機能を有効にするため、Twitter側に専用のリストを作成します。
準拠するリストが既にあればそちらを使っても構いません。
なお、使えるリストはアカウントで作成したもののみです。

* twitterリスト: normal
  フォロワー監視をおこなうユーザをリストします。
  ここで登録したユーザしかフォロワー監視をおこないません。
* twitterリスト: un_refollow
  フォロワー監視で自動リムーブしたユーザをリストします。
  ここに登録されたユーザはキーワード検索や、新規ユーザ出力でひっかからなくなります。



<a id="iDefEncode"></a>
## デフォルトエンコードの確認　★初回のみ
本ソフトはデフォルトエンコード**utf-8**で動作することを前提に設計してます。
utf-8以外のエンコードでは誤動作を起こす場合があります。
pythonのデフォルトエンコードを確認したり、utf-8に設定する方法を示します。

```
# python
>>> import sys
>>> sys.getdefaultencoding()
'utf-8'
  utf-8が表示されればOKです。

>> exit
  ここでCtrl+Z を入力してリターンで終了します。
```

もしutf-8でなければWindowsの環境変数に PYTHONUTF8=1 を追加します。
「スタート」→「システムの詳細設定 で検索」→「詳細設定」→「環境変数」
ここに **変数名=PYTHONUTF8、変数値=1** を追加する。
設定したら上記エンコードの確認を再実行して確認しましょう。




<a id="iGetTwitter"></a>
## Twitter APIの取得方法　★初回のみ
1.以下、twitterのサイトにtwitterアカウントでログインします。
　　[Twitter API](https://apps.twitter.com/app/new)

2～5 までの項目ではDeveropper Accountの設定をおこないます。
  ※設定済なら6へ進む

2.「Create an app」をクリックします。

3.HObby list→Making botをクリックしてNextを押します。

4.各項目を入力し、Nextを押します。
　**bot登録するには電話番号を登録する必要があります。**「Add a valid」で登録します。
　What country do you live in? はJapanを選択します。
　What would you like us to call you? はDeveropper Accountでのユーザ名（英数字）を入力します。
　Want updates about the Twitter API? は必要に応じてチェックします。

5.各項目にbotを作成する用途を英語で入力していきます。ここで入力した内容でTwitterの審査を受けることになります。
　botの目的をはっきり説明しないと審査が通らない場合があるようです。
　英語で入力するように言われてますが、日本語でもばっちり大丈夫です。
　このbotを利用するときは以下のように入力してください。

**In your words**
主にフォロワーの管理をおこなうためのbotで利用します。
フォロワーやいいねされる数を増やすため、こちらから他の方のフォローやいいねを増やしたいと考えております。しかし、検索窓では自分が意図するユーザを見つけるのは手間がかかります。また、フォローしたとしても中にはフォローされるのを嫌がったりの理由でリフォローを貰えないユーザさんがいるかもしれません。何らかの理由でいつの間にかフォローを解除されているかもしれません。また、いいねをし続けることでいいねリストが一杯になり、整理がつきにくくなってしまうかもしれません。

以下のような機能をもちます。

●botに入力したパターンのツイートをしたユーザを抽出します。
自分が意図するユーザを見つけるため、事前に自分が気にするワードをbotに入力します。たとえば、現時刻から1時間前までのタイムラインから、「マインクラフト」という文字を含めたツイートをしたユーザなどです。文字の抜き出しは、pythonのStrings関数や、IndexOf関数を使用します。
抽出したユーザ情報はCSV形式にしてローカルPCに出力します。CSVはユーザ名と、ユーザのプロファイルリンクが表示できるようにします。
--------------------
検索ワード：マインクラフト,,
username,prof_url,last tweet,
lucida3poi,https://twitter.com/lucida3poi,2020-09-20 08:00:00+0900,
lucida3hai,https://twitter.com/lucida3hai,2020-09-20 08:10:00+0900,
......
--------------------
ただし、過去にアンフォローしたユーザは抽出から除外されます。アンフォローしたユーザについては以降で説明させていただきますが、説明通りに従うと"un_follow"に含まれるユーザが除外ユーザになります。これは、"フォローのしつこさ"の解消を目的としています。
botの収集動作としてはここで完結します。
フォロー動作はbotからおこないません。上記CSVに抽出したユーザリンクをクリックして、ブラウザを開かせ、目でTwitterプロフィールを確認してフォローするかを決めるようにします。フォローはTwitter上の「フォロー」ボタンをクリックでさせます（手動で）。
botがこのCSVをTwitter上、その他外部に公開することはありません。
●一定期間を過ぎた、いいねの解除をします。
既に付けた"いいね"のうち一定期間を過ぎたものを"いいね解除する"します。例えば、現時刻から3日を超えた時点でつけたいいねを解除したりです。
botでいいねを付けることはありません。
●一定期間を過ぎた、非リフォロワーのアンフォローします。
フォローしているユーザのうち、一定期間を過ぎてもリフォローされないユーザをアンフォローします。例えば、フォローしてから3日を超えた時点でフォローされていないユーザを自動でアンフォローします。同時に、アンフォローしたユーザは、わかりやすいようにリストに登録します。ここで登録するリストもbotで設定できます。例えば"un_follow"というリストに追加します。
ここで追加されたユーザは次回の抽出から除外されます。botから自動でフォローすることはありません。
●実行の規制をおこないます。
Twitterへの負荷を軽減するため、実行間隔をbotで制御します。たとえば、bot実行したとき、前回の実行が10分前であったら以降の処理を行わず、botの動作を停止します。10分を過ぎた実行は処理されます。この仕様によって手動実行でもcronによる定期実行でも対応できる上、Twitterサーバへの負荷が少なくなると考えてます。

**Are you planning to analyze Twitter data?**
分析というより、ツイートやユーザの抽出、絞り込みをおこないます。ユーザの抽出、絞り込み動作については、上記「botに入力したパターンのツイートをしたユーザを抽出します。」の回答を参照ください。なお、botが収集したデータをTwitter上、その他外部に公開することはありません。

**Will your app use Tweet, Retweet, like, follow, or Direct Message functionality?**
タイムラインをロードする機能、フォロー一覧をロードする機能、フォロワー一覧をロードする機能、いいね一覧をロードする機能、指定のいいねを解除する機能、指定ユーザをアンフォロー機能、指定ユーザをリスト（過去にアンフォローされたユーザ）へ追加する機能は使います。いいね機能や、リスト機能の使われ方については、上記「In your words」の回答をご参照ください。

**Do you plan to display Tweets or aggregate data about Twitter content outside of Twitter?**
botの利用はビジネス目的のツイート分析ではなく個人の利用を目的としています。詳しい分析方法については、上記「In your words」の回答をご参照ください。

**Will your product, service or analysis make Twitter content or derived information available to a government entity?**
このbotで作成されたデータやCSVを政府機関に提示することは考えてませんが、要求があれば提出できると思います。


Nextを押します。「Looks good!」を押します。

6.規約を読み、By clicking on the box～のボックスをチェックして「Submit Application」をクリックします。

7.Twitterに登録されたメールアドレスに確認メールが送られていますので、「Confirm your email」をクリックします。
　利用開始は審査結果メールを受けてからになります。メールが来るまでお待ちください。1日くらいで返事がきます。
　なお前提条件にあったとおり、何度もしつこく質問されると思いますが、根気よく回答してあげてください。


汗かきながら書いたメールのやりとりが上手くいき、審査に受かると、Twitterから
「Your Twitter developer account application has been approved!」の開発許諾メールを受けとれます。
おめでとう！これでようやく次に進めます。

6.メールをクリックして、Welcome to the Twitter Developer Platformでアプリ名を入力します。
　アプリ名は後でdashbordで変えられます。

7.以下をメモします。**この情報は厳重に保管してください**

* API key
* API secret key
* Bearer token

8.[Skip to dashboard]をクイックし、[Yes, I saved then]をクリックします。
　以後はdashbord画面で管理します。

9.Setting画面で必要事項を入力します。

**App Details**
App name
　変える場合入力する。
Description
　アプリの説明。わかりやすいように。
App permissions
　Read and Write　を指定してください。

**Authentication settings**
Enable 3rd party authentication
　有効にしてください。
Callback URLs
　必須。コールバックしませんが自分のブログURLなど適当でいいです。（他人のサイトURLは絶対ダメ！）
Website URL
　必須。https://github.com/lucida3rd/lucibot_win　などにしておくと、botの説明に飛べます。（わたしのgithubです）

10.keys and tokensに切り替えます。**この情報は厳重に保管してください**
Authentication TokensのAccess Token & Secretの[Generate]をクリックして以下をメモします。

* Access token
* Access token secret

4つの情報はあとで設定します。

* API key
* API secret key
* Access token
* Access token secret

> 最悪忘れてしまってもリセットして取り直すことができます。
> ただキーを流出させるのはリスクが大きすぎるので注意しましょう。




<a id="iSetup"></a>
## セットアップ手順

1.pythonと必要なライブラリをインストールします。

インストーラを以下から取得します。基本的に * web-based installer を使います。
入手したインストーラで好きな場所にセットアップします。
  [python HP](https://www.python.org/)

Add Python x.x to Path はチェックしたほうがいいです。
その他はデフォルトか、環境にあわせてオプションを選択しましょう。
インストールが終わったらテストしてみます。

```
# python -V
Python 3.8.5
  ※Windowsの場合、python3ではなく、pythonらしいです

# pip3 install requests requests_oauthlib psycopg2
～中略～

# pip3 list
～以下省略～
```

2.postgreSQLをインストールします。

2-1.インストーラを以下から取得します。  
　　[postgresql HP](https://www.postgresql.org/download/)
　Windows 32bit or 64bit 形式を選択します。

2-2.インストーラに従ってインストールします。
　postgreSQLのスーパーユーザは postgres になります。
　**パスワードは忘れずに覚えておきましょう**
　スタックビルダは必要に応じてセットアップしてください。（特に不要です）

2-3.環境変数を設定します。
「スタート」→「システムの詳細設定 で検索」→「詳細設定」→「環境変数」
ここのPathにpostgreSQLのbinフォルダを追加します。
# C:\Program Files\PostgreSQL\13\bin とか
追加したらOKを押します。

2-4.動作テストします。

```
# psql --version
psql (PostgreSQL) 13.0

psql -U postgres

=>

=> \q
　※エラーがでなければOKです
```

2-5.Lucibotで使うデータベースを作成します。

```
# createuser -U postgres lucibot
# createdb -U postgres -O lucibot lucibot
パスワードはスーパーユーザ[postgres]のものです

スーパーユーザ[postgres]でログインする
# psql postgres -U postgres

データベースのパスワードを設定する。
=> alter role lucibot with password '[DBパスワード]';
=> alter role lucibot with login;
=> \q  
この操作でDBのユーザ名、データベース名は lucibot になります。

# psql -U lucibot lucibot
[DBパスワード]でログインする

=>

=> \q
　※エラーがでなければOKです
```

3.botソースの管理アプリとしてWindows版のgithubデスクトップを使います。

3-1.githubデスクトップをインストールします。
　　[githubデスクトップ](https://desktop.github.com)

3-2.githubの自分のアカウントに本家リポジトリをFork（コピー）する。
　　[Lucibotリポジトリ](https://github.com/lucida3rd/lucibot_win)
  の右上あたりの[Fork]ボタンを押してください。
  すると、自分のアカウントに[自垢名 / lucibot_win]というリポジトリができます。

3-3.githubデスクトップで1項でForkしたリポジトリから自PCにクローンをダウンロードします。
  githubデスクトップのCurrent repository→Add→Cloneを選択します。
  任意のフォルダを選択してCloneを押してください。

3-4.自分のブランチを作ります。
  githubデスクトップのCurrent branch→New branchで任意の名前を入力します。



<a id="iUpdate"></a>
## アップデート手順
るしぼっとリポジトリのmasterから最新版をpullする方法です。  

1.githubデスクトップを起動します。

2.自分のLucibotリポジトリを選択し、Current branchをクリックします。

3.New branchをクリックし、バックアップ用のブランチを作成します。
  名前はわかりやすいように。

4.ブランチを[main]に切り替えます。

5.[Fetch Origin]をクリックします。

6.[Puch]をクリックします。

ここまでで、自分のリポジトリの[main]と、自PCのソースに最新が反映されてます。

もし不具合があったら...？
3項で保存したブランチに切り替えると、自PC側にアップデート前のソースが戻ってきます。
以後、アップデートがあったら[main]に切り替えて[Fetch]すれば、修正後のソースが反映されます。




<a id="iStart"></a>
## 起動方法
DOSのコマンドラインにて以下を入力します。初回は手順1から実施してください。

1.初期設定します。
```
# cd [Lucibotのインストールフォルダ]
# python run.py init
```

初回はデータベースの全初期化と、ユーザ登録を実施します。画面に従って入力します。
以下の情報が必要となります。

* lucibotのデータベースパスワード
* Twitterアカウント名
* Twitter Devで取ったAPI key
* Twitter Devで取ったAPI secret key
* Twitter Devで取ったAccess token
* Twitter Devで取ったAccess token secret

また入力途中、リストの設定があります。画面に従って設定してください。
ここで設定しないと、自動リムーブができません。
リストの作成はTwitter側でおこないます。
* normalリスト
  フォロワー監視を行うユーザのリストを選択します。
* un_followerリスト
  自動リムーブしたユーザを登録するリストを選択します。

2.Lucibotを起動します。
```
# cd [Lucibotのインストールフォルダ]
# python run.py [twitterアカウント名] [lucibotのデータベースパスワード]
```

起動すると、コンソール画面が起動します。




<a id="iFunction"></a>
## 機能説明
Lucibotの各機能を以下に説明します。
コマンドを実行するには、画面のプロンプトに指定のコマンドを入力します。
コマンドは全て\マークの後、半角英字を入力します。


<a id="iFunc_GetInfo"></a>
#### 監視情報取得機能【 \g 】
Twitterでおこなっているいいね、フォロー、フォロワーの状態を取得します。
取得したあとデータベースに保存され、あとで閲覧することができます。


<a id="iFunc_GetInfo"></a>
#### キーユーザフォロー(手動)【 \f 】
監視情報取得で取得したキーユーザのなかから、候補ユーザをフォローします。
今までフォローしたことがなくて、興味があいそうなユーザをフォローできます。
フォローは手動で指示しておこないます。


<a id="iFunc_Iine"></a>
#### いいね情報 / 監視【 \vi / \ri 】
データベースに記録されているいいね情報を閲覧します。
現在リムーブ済みのいいねも、30日間は閲覧可能です。
いいね監視は2日前のいいねを自動でリムーブします。


<a id="iFunc_Follower"></a>
#### フォロワー情報 / 監視【 \vf / \rf 】
データベースに記録されているフォロワー情報を閲覧します。
現在アンフォロワー、片フォローのユーザの情報も閲覧できます。
フォロワー監視は、normalリストに登録されているユーザをフォローしてから5日以内にリフォローされなかった場合、自動でリムーブします。


<a id="iFunc_Keyword"></a>
#### ツイート検索【 \s 】
直近数時間のうち指定したキーワードのツイートを画面に表示し、表示したユーザの一覧をCSVで出力します。
キーユーザCSV出力と違って単体のキーしか検索できませんが、APIの消費が少なくて済みます。


<a id="iFunc_Keyword"></a>
#### キーユーザCSVの出力【 \k / \cs 】
直近数時間のうち指定したキーワードのツイートしたユーザの一覧をランダムにCSVで出力します。
今までフォローしたことがなくて、興味があいそうなユーザを検索する機能です。
un_followerに入っているユーザ、今まで一度でもフォロー、リムーブしたユーザは含みません。
データの取得は、監視情報取得でおこないます。検索の条件は、キーユーザ検索の変更からおこないます。


<a id="iFunc_Keyword"></a>
#### ユーザ復活【 \cr 】
自動リムーブでリムーブしたユーザとのフォロー関係を修復します。
Twitter ID(screen_name)を入力すると、条件によってはフォローの関係を復活できます。


<a id="iFunc_CSV"></a>
#### フォロワーCSVの出力 / 全ユーザCSV【 \f / \fa 】
新規のフォロワーをCSVで出力します。
un_followerに入っていないユーザ、今まで一度でもフォロー、リムーブしたことがないユーザが選出されます。
全ユーザCSVは、データベースに登録されているフォロワー情報を全てCSVで出力します。
★現在オミットになってます



<a id="iDisclaimer"></a>
## 免責事項
* アーカイブなどに含まれるファイル類は消したりしないでください。誤動作の原因となります。
* 当ソースの改造、改造物の配布は自由にやってください。その際の著作権は放棄しません。
* 未改造物の再配布は禁止とします。
* 当ソースを使用したことによる不具合、損害について当方は責任を持ちません。全て自己責任でお願いします。
* 当ソースの仕様、不具合についての質問は受け付けません。自己解析、自己対応でお願いします。
* 使用の許諾、謝辞については不要です。
* その他、ご意見、ご要望については、Twitterに記載してある"マシュマロ"までお送りください。




<a id="iReference"></a>
## 参考記事　※敬称略
* [Windows 上の Python で UTF-8 をデフォルトにする（methane）](https://qiita.com/methane/items/9a19ddf615089b071e71)




