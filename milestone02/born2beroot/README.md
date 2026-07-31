_This project has been created as part of the 42 curriculum by kyonaha._

## Description
このプロジェクトは、仮想マシンの構築を通してシステム管理の基礎的な要素を学ぶことを目的としています。目標は、GUIを持たないセキュアなDebianサーバーを構築し、LVMによる厳格なパーティション設計、強化されたセキュリティフレームワーク、厳密なユーザー/sudo管理、ファイアウォール制限、そして自動化された監視システムを実装することです。

## Project description

### 1. Conceptual Overview
* **仮想マシン（VM）の仕組み：** VMは物理コンピュータをソフトウェアでエミュレートしたものです。ハイパーバイザーによって物理ハードウェア（ホスト）から抽象化・分離された層の上で、OS（ゲスト）を動作させます。
* **仮想マシンの目的：** VMを使うことで、リソースの効率的な利用、サンドボックス環境でのテスト、クローン作成やスナップショットによるロールバックが容易になり、1台の物理マシン上で複数の独立したOSを実行できます。
* **LVMの仕組み：** LVM（論理ボリュームマネージャー）は物理ストレージデバイスを抽象化します。複数の物理ディスクをボリュームグループ（VG）としてプールし、それを論理ボリューム（LV）に分割します。これにより、生のディスクを再パーティションすることなく、パーティションを動的にリサイズできます。

### 2. Technical Comparisons

| 比較項目 | 選択肢A（採用） | 選択肢B |
| :--- | :--- | :--- |
| **オペレーティングシステム** | **Debian：** 非常に安定しており、予測可能なリリースサイクル、大きなコミュニティ、軽量な最小構成インストールが可能。基礎学習に最適。 | **Rocky Linux：** RHEL系ディストリビューション。エンタープライズ向けで、デフォルトでSELinuxとfirewalldを使用。セットアップが複雑。 |
| **パッケージマネージャー** | **apt：** 高レベルなパッケージ管理ツール。ユーザーフレンドリーな出力で、Debian系システムの標準。 | **aptitude：** より高度で、テキストベースのUI（TUI）を備え、複雑な依存関係の解決に優れている。 |
| **セキュリティフレームワーク** | **AppArmor：** パスベースのアクセス制御。特定のプログラムパスに紐づくプロファイルを使ってシステムの権限を制限するため、設定が容易。 | **SELinux：** ラベルベースの強制アクセス制御（MAC）。非常に細かく制御できるが、すべてのファイル・プロセスにセキュリティコンテキストを割り当てる必要があり、極めて複雑。 |
| **ファイアウォール** | **UFW：** Uncomplicated Firewall。iptables/nftablesのユーザーフレンドリーなフロントエンドで、標準的なルール作成がシンプル。 | **firewalld：** ゾーンベースの動的ファイアウォールデーモン。高度なネットワーク環境やステートフルなルールに対応。 |
| **仮想化ソフト（Hypervisor）** | **VirtualBox：** Oracle製のType-2ハイパーバイザー。Windows／Intel Mac／Linuxで広く使われており、安定していて資料も豊富。 | **UTM：** QEMUベースのハイパーバイザー。Apple Silicon（M1以降）ホストにネイティブ対応しており、VirtualBoxが事実上サポートしないARM Mac環境では必須の選択肢となる。 |

---

### 3. Design Choices & Security Policies
* **仮想化ソフトの選定：** 開発機がIntel Macであるため、資料が豊富で安定性の高いVirtualBoxを採用した。なお、Apple Silicon（M1/M2/M3）ホストの場合はVirtualBoxが実質的にサポートされないため、QEMUベースのUTMを選択する必要がある。
* **パーティショニング：** 保存データを保護するため、LVMを利用した暗号化パーティションを構成。暗号化された物理ボリューム（`sda5_crypt`）内に、専用のroot（`/`）ボリュームと動的な`[SWAP]`領域からなるシンプルで最小限のレイアウトを構築し、プロジェクトの厳格な必須セキュリティ要件を完全に満たしている。
* **パスワードポリシーの利点：** 最小文字数、文字種の多様性、有効期限に関するパラメータを強制することで、ブルートフォース攻撃やクレデンシャルスタッフィング攻撃の対象範囲を大幅に減らせる。
* **パスワードポリシーの欠点：** 厳格な定期変更は「パスワード疲れ」を招き、ユーザーが複雑な文字列をメモに書き留めたり、予測可能な連番パターンを使用したりする原因になり得る。
* **Sudo制約：** コマンド実行経路（`secure_path`）を制限し、TTY経由での実行を必須化、パスワード入力ミスの許容回数を3回に制限、そして`/var/log/sudo/`への出力・入力の集中ログ記録を設定。

---

## Instructions

### 1. 簡易セットアップとサービスの確認
* **GUIが動作していないことを確認：**
  VMがCLI（コマンドラインインターフェース）で直接起動することを確認する。`X.org`、`Wayland`、デスクトップマネージャーが動作していないこと。
* **OSバージョンの確認：**
  ```bash
  head -n 2 /etc/os-release
  ```
* **AppArmorのステータス確認：**
  ```bash
  sudo systemctl status apparmor
  ```
* **UFWのステータス確認：**
  ```bash
  sudo systemctl status ufw
  ```
* **SSHサービスのステータス確認：**
  ```bash
  sudo systemctl status ssh
  ```

### 2. パスワードポリシーとユーザー管理
* **パスワード複雑性ポリシーの確認（PAM）：**
  ```bash
  sudo cat /etc/pam.d/common-password
  ```

* **パスワード有効期限ポリシーの確認：**
  ```bash
  sudo cat /etc/login.defs
  ```

* **ユーザーへの有効期限ポリシー適用状況を確認：**
  ```bash
  sudo chage -l user 
  ```
* **ログインユーザーが存在すること、その所属グループを確認：**
  ```bash
  id user
  ```
* **新規ユーザーの作成：**
  ```bash
  sudo adduser new_user
  ```
* **新規グループの作成：**
  ```bash
  sudo addgroup new_group
  ```
* **ユーザーをグループに割り当てる：**
  ```bash
  sudo usermod -aG new_group new_user
  ```
* **新規ユーザーの所属グループを確認：**
  ```bash
  id new_user
  ```

### 3. ホスト名とパーティションの確認
* **現在のホスト名を確認：**
  ```bash
  hostname
  ```
* **指定されたホスト名に変更：**
  ```bash
  sudo hostnamectl set-hostname <assigned_name>
  ```
* **変更を反映させるために再起動し、確認：**
  ```bash
  sudo reboot
  ```
* **確認後、ホスト名を元の形式に戻す：**
  ```bash
  sudo hostnamectl set-hostname old_hosname
  sudo reboot
  ```
* **LVMパーティション構成を確認し、サイズ設定を比較：**
  ```bash
  lsblk
  ```

### 4. Sudoポリシーとログ監査
* **Sudoが正しくインストールされていることを確認：**
  ```bash
  sudo -V
  ```
* **厳格なsudoルールファイルの実装を表示：**
  ```bash
  sudo visudo
  # または visudo 経由で確認
  sudo cat /etc/sudoers.d/sudo_config
  ```
* **sudoログディレクトリが存在し、有効なログが記録されていることを確認：**
  ```bash
  ls -l /var/log/sudo/
  ```
* **ログが更新されることを確認するため、任意のコマンドをsudoで実行：**
  ```bash
  sudo apt update
  ```
* **`/var/log/sudo/`内の履歴と出力が動的に更新されたことを確認：**
  ```bash
  sudo cat /var/log/sudo/sudo.log
  ```

### 5. UFWファイアウォールの設定
* **有効なUFWルールを一覧表示：**
  ```bash
  sudo ufw status numbered
  ```
* **ポートを開放する新しいルールを追加：**
  ```bash
  sudo ufw allow 1000/tcp
  ```
* **ポートが正常に追加されたことを確認：**
  ```bash
  sudo ufw status
  ```
* **作成したルールを削除：**
  ```bash
  sudo ufw delete allow 1000/tcp
  ```
* **ファイアウォールが元の状態に戻ったことを確認：**
  ```bash
  sudo ufw status
  ```

### 6. SSHの制約
* **SSHの設定ポート先を確認：**
  ```bash
  sudo grep -i "Port" /etc/ssh/sshd_config
  ```
* **SSH経由でのRootログイン設定を確認：**
  ```bash
  sudo grep -i "PermitRootLogin" /etc/ssh/sshd_config
  ```
* **ホストマシンのターミナルから、新規作成したユーザーでSSHログインをテスト：**
  ```bash
  ssh new_user@127.0.0.1 -p 4242
  ```

### 7. スクリプトのモニタリングとCronスケジュール
* **シェルスクリプトの実装内容を表示：**
  ```bash
  sudo cat /usr/local/bin/monitoring.sh
  ```
* **rootのcrontabスケジュールを確認：**
  ```bash
  sudo crontab -l
  ```
* **スクリプトの実行間隔を1分に変更：**
  ```bash
  sudo crontab -e
  # 変更前： */10 * * * * /usr/local/bin/monitoring.sh
  # 変更後： */1 * * * * /usr/local/bin/monitoring.sh
  ```
* **確認後、cronの実行間隔を10分に戻す：**
  ```bash
  sudo crontab -e
  # 元に戻す： */10 * * * * /usr/local/bin/monitoring.sh
  ```

---

## Resources
* **参照した公式ドキュメント：** 
Debian GNU/Linux インストールガイド、Linux manページ

* **AIの使用：** 
READMEの作成補助、セットアップ中に生じた概念的な疑問の学習・整理に使用した。

* **参考にしたウェブサイト：** 
SELinuxの基本を理解する
"https://qiita.com/Brutus/items/7d026929f393b0ec25d0"