# 法務部行政執行署案管小工具

這是一套針對行政執行署案件管理系統設計的小工具套組，用來減少執行署大量且重複的工作。
這套工具的工作流程是：
1. 讓使用者用更簡潔的方式填寫案管系統某些頁面的表格。
2. 獲取案管系統回覆的內容。
3. 經過處理後包裝成本機的表格或文件檔，讓使用者用自己習慣的工具和方式使用資料。

因此，這份案管小工具有機會做到的是：
* 獲取手動操作案管系統能夠直接獲得的資料，例如查詢財產清冊、查詢綜合畫面、查詢辦案進行簿等。
* 自動獲取手動操作案管系統能獲取的資料，並加以運算或格式化輸出，例如自動列印財產清冊、自動判讀並精簡化財產清冊、自動判斷終結情形並報結等。

從上可知，案管小工具現在沒有、以後也沒辦法做到：
* 獲取他人的帳號與密碼。
* 存取自己的帳號無權限獲得的資訊。
* 直接存取或寫入案管系統的資料庫。
* 直接操作案管系統的主機。

## 開發環境

這套工具基於下述平台開發與測試：

- Windows 7 Professional (32 Bit)
- 4GB RAM
- 嘉義分署案管系統 (截至 2018/08/24 的版本)

若使用環境與開發環境不同，可能會有部分功能產生非預期的結果，如：

- **若所在分署不同，因為函稿編號不同，包含自動判斷函稿功能的程式可能會失效**。
- 若案管系統版本更新且介面發生變動，可能導致舊有的溝通接口失效。
- 若主機規格低於開發環境，可能發生記憶體不足、或運算過慢導致列印功能失效等錯誤。

## 安裝指南

1. 安裝 Python 3。
    1. 獲取 `Python 3` 的最新安裝程式。
        - 請至 [Python 官方網站](https://www.python.org/)下載。
        - 如果沒有外部網路權限，你可能會需要請網路管理人員協助。
    2. 執行安裝檔後，勾選 `Add Python 3.x to PATH` 後，點選 `Customize installation`。
    3. 在 `Optional Features` 頁面，勾選 `pip` 後其餘留白，再點選 `Next` 鍵。
    4. 在 `Advanced Options` 頁面不更改任何預設選項，直接點選 `Install` 鍵。
        - 安裝過程中可能會需要外部網路權限。

2. 獲取案管小工具程式程式碼。
    1. 到[案管小幫手專案頁面](https://github.com/b821213/Enforcement-Agency-Case-Management-Tools)點選頁面上字樣為 `Clone or download` 的綠色按鈕。
    2. 點擊 `Download ZIP` 按鈕。
    3. 將獲得的檔案解壓縮到你自己喜歡的資料夾內，或者直接修改解壓縮結果的資料夾名稱。
    4. 最後的結果應為一個包含許多 .py 副檔名檔案的資料夾。

3. 將 `cmd.exe` 複製到案管小工具的所在資料夾內。
    1. 在 `C:\Windows\System32` 內找到名為 `cmd.exe` 的檔案。
        - 如果你的電腦設定不會顯示已知類型的副檔名，這個檔案可能檔名僅會顯示為 `cmd`。
    2. 將該檔案複製到案管小工具的所在資料夾內。

4. 初始化案管小工具的設定。
    1. 打開案管小工具所在資料夾內的 `cmd.exe`。
    2. 鍵入 `python configure.py` 並且點擊 `Enter` 鍵執行。
    3. 依據程式提示的內容依序鍵入程式要求的資料。
        - 案管主機 IP 即為瀏覽器上案管系統網址列顯示的形如 `xxx.xxx.xxx.xxx` 的部分，其中 `xxx` 為 `0~255` 間的數字。如：`192.168.0.1`、`172.123.45.56`等。
        - 程式會依序詢問使用者執行人員、檔管人員、統計人員的帳號 (與密碼)，使用者僅須在詢問到自己身分時鍵入自己的帳號與密碼即可，其他非自己身分的問題可以直接按 `Enter` 鍵跳過。
        - 例如：執行人員僅需在第一個問題 (詢問執行人員帳號與密碼) 時鍵入帳號資料，接下來的兩個問題都直接按 `Enter` 跳過即可；檔管人員的第一個問題可以直接按 `Enter` 跳過，在第二個問題時鍵入自己的帳號資料，接著再次跳過第三個問題即可。
    4. 如果使用者同時具備多種人員的資料，也可以回答其中的複數個問題。設定完成後，只有那些有被鍵入對應權限人員資料的功能可以正常使用。

## 功能一覽

執行股相關功能：

| 功能名稱 | 程式名稱 |
| -------- | -------- |
| [進度一點通](#auto_readpy-進度一點通) | auto_read.py |
| [財冊小秘書](#get_asset_statspy-財冊小秘書) | get_asset_stats.py |
| [結案土撥鼠](#get_clear_casespy-結案土撥鼠) | get_clear_cases.py |
| [待扣存名單](#get_detainable_listpy-待扣存名單) | get_detainable_list.py |
| [大戶雷達儀](#get_vippy-大戶雷達儀) | get_VIP.py |
| [報結機器人](#goodbye_casespy-報結機器人) | goodbye_cases.py |
| [併卷小幫手](#merge_helperpy-併卷小幫手) | merge_helper.py |
| [自動印財冊](#print_assetpy-自動印財冊) | print_asset.py |
| [自動 508](#print_bank_responsepy-自動-508) | print_bank_response.py |
| [案號生成器](#range_list_genpy-案號生成器) | range_list_gen.py |
| [反報機器人](#regret_casespy-反報機器人) | regret_cases.py |

檔管室相關功能：

| 功能名稱 | 程式名稱 |
| -------- | -------- |
| [年度歸檔冊](#get_ended_case_listpy-年度歸檔冊) | get_ended_case_list.py |
| [應銷統計表](#get_todestroy_statspy-應銷統計表) | get_todestroy_stats.py |

統計室相關功能：

| 功能名稱 | 程式名稱 |
| -------- | -------- |
| [Key 金額列表](#print_daily_payment_listpy-key-金額列表) | print_daily_payment_list.py |

## 使用說明

### 執行程式

打開案管小工具的所在資料夾內的 cmd，鍵入指令 `python [程式名稱] [相關參數]`，然後按下 `Enter` 鍵，便會開始執行程式。如果鍵入的格式有誤，或者忘記需要輸入哪些參數，也可以直接執行 `python [程式名稱]`，畫面上即會提示正確的輸入格式。

### 檔案格式

案管小工具中，大部分時候，使用者要提供給程式的資訊都是先輸入到 Excel 文件內、儲存成檔案後，再把檔案的路徑做為參數傳給程式；類似地，程式要回饋給使用者的資訊也都是直接存成 Excel 或者文件編輯器可以讀取的檔案，使用者再自行去開啟/閱讀檔案。

程式讀取的輸入檔一律以 .csv 檔儲存，使用者可以在 Excel 內打完資料後於存檔時選擇此檔案類型。除報結機器人 (`goodbye_cases.py`)、反報機器人(`regret_cases.py`) 外，其餘程式皆共用如下的輸入檔格式。
輸入檔依據輸入內容的不同，分成兩類：

1. 以執行案號作為輸入內容。
    - 每筆輸入資料對應到一列，每列占 Excel內的 A, B, C 三欄，內容分別為該筆資料的執行年度、案件類別與案號。
    - 類別與案號的皆不須填入前導 0 (填寫亦無妨)，任兩筆資料間應避免有多餘的空白列。

  **範例**

  | | A | B | C |
  | --- | --- | --- | --- |
  | 1 | 106 | 3 | 123456 |
  | 2 | 107 | 1 | 13 |
  | 3 | 99 | 4 | 88888 |

2. 以統一編號作為輸入內容
    - 每筆輸入資料對應到一列，每列占 Excel 內的 A 一欄，內容即是義務人的統一編號。
    - 任兩筆資料間應避免有多餘的空白列。

  **範例**

  | | A |
  | --- | --- |
  | 1 | A123456789 |
  | 2 | B123456789 |
  | 3 | C123456789 |

**兩種輸入內容不可在同一份檔案內混合使用**，否則程式讀取輸入時會遭遇錯誤而無法執行。

部分情況下 (如已經使用案號生成器產生某區間內所有案號)，使用者可能僅須使用輸入檔內的部分資料，此時可在這些資料列末欄的下一欄 (若輸入為案號，則為 D 欄；若輸入為統一編號，則為 B 欄) 輸入「非半型逗號的任意非空白字串」註記。
  - 若輸入檔內有任何一列有註記，則僅有被註記列內的資料會被視為輸入內容；否則所有資料都會被視為輸入內容。
  - 註記用的「任意非空白字串」毋須一致。舉例而言，在某些列的末欄填入「yes」而在另外一些列的末欄填入「n」，則兩者都會被視為輸入內容。

**範例 1**

| | A | B | C | D |
| --- | --- | --- | --- | --- |
| 1 | 106 | 3 | 123456 | v |
| 2 | 107 | 1 | 1 | |
| 3 | 99 | 4 | 88888 | v |
| 4 | 105 | 2 | 13579 | |
| 5 | 104 | 3 | 168168 | x |
| 6 | 103 | 1 | 7122 | no |

上表中的第 1、3、5、6 行的資料都會被視為輸入內容傳給程式，其餘行則不會。

**範例 2**

| | A | B |
| --- | --- | --- |
| 1 | A123456789 | |
| 2 | B123456789 | test |
| 3 | C123456789 | 我全都要 |
| 4 | D123456789 | |
| 5 | E123456789| 這個我要 |
| 6 | F123456789 | |

上表中的第 2, 3, 5 行的資料都會被視為輸入內容傳給程式，其餘行則不會。

## 功能細節

以下的指令格式欄位中，以中括號 `[]` 包含的部分請代換成括號內說明檔案的名稱，以小括號 `()` 包含的部分則是該檔案應使用的副檔名。

舉例而言，指令格式為

`python auto_read.py [輸入檔名 (.csv)] [輸出檔名 (.csv)] [紀錄檔名 (.csv)]`

則使用時指令可能會是：

`python auto_read.py input.csv output.csv error.csv`

其中 `input.csv` 是輸入檔的檔名，必定要是既存的檔案；`output.csv`、`error.csv` 則是程式產生的輸出檔與紀錄檔，若原先檔案不存在程式會自動生成，原先已經存在則會被覆蓋成新的內容。所有檔案的命名都可以由使用者自由命名，不影響程式的功能。

### 執行股相關功能

#### auto_read.py (進度一點通)

指令格式：`python auto_read.py [輸入檔名 (.csv)] [輸出檔名 (.csv)] [紀錄檔名 (.csv)]`

支援輸入格式：案號、統編

**注意：若函稿編號與嘉義分署不同，自動判斷是否分期中的功能將會失效。**

自動判讀辦案進行簿，可快速判斷案件當前狀況 (分為四種：已掛結、已報結、分期中、其他，由於案件多為其他故若屬其他則該欄顯示空白)，並列出經判讀後最新的數個執行動作，每個動作皆另外分析出製稿主案號、電子文號等屬性；若為動作為電子發文且已電子交換，在動作一欄的最後會附註電子交換日期，方便檢視公文是否已發出。

執行程式後會詢問使用者，針對以案號輸入的案件，要查詢的標的是輸入的案件本身，還是該案件義務人的主案件。如果所有輸入內容皆為統一編號而非案號，則此選項不影響輸出內容。

目前預設會列出最新的 5 個執行動作，若須修改列出的數量，請修改 `configs.py` 內的 `n_show_situ_items` 值。

若輸入內容為統一編號，或者輸入內容為案號但是選擇查詢主案件，則依照下列方式找出代表號，再依據該代表號進行查詢與分析：

  1. 若輸入為案號，則先透過綜合畫面查詢該案號獲得義務人統一編號。
  2. 透過綜合畫面查詢義務人統一編號，找出義務人在本股 (以 `configs.py` 內的 `default_dept` 為準) 稅執、罰執、非勞保費執的最早案件，最多共三件。
  3. 若以上的案件皆未有執行動作，則提示「查無已執行案件」錯誤訊息。
  4. 否則取以上三件的執行動作中最新者的主案號，做為義務人代表號。

查詢過程中若因為各種原因出錯，錯誤訊息會被記錄在給定的紀錄檔案內。

#### get_asset_stats.py (財冊小秘書)

指令格式：`python get_asset_stats.py [輸入檔名 (.csv)] [輸出檔名 (.csv)] [紀錄檔名 (.csv)]`

支援輸入格式：案號、統編

查義務人財產清冊並自動分析，每個來源僅留下最新且等於超過 450 元的資料 (若幣值為外幣，則依據案管系統提供的匯率進行換算)。若義務人有多人 (如共同繼承人、獨資商號代理人)，則以案管在辦案進行簿提供的義務人資料為準全數送到財冊頁面進行查詢，獨資與合夥則另外在義務人名稱前標註。

財冊查詢起始日參照 `configs.py` 內的 `asset_date_begin` 變數，由民國年月日組成共 7 碼，如 97 年 1 月 31 日為 `0970131`，107 年 6 月 1 日為 `1070601`。此變數與自動印財冊 (`print_asset.py`) 共用，若兩者要求日期不同則須在每次切換時修正此變數。

查詢過程中若因為各種原因出錯，錯誤訊息會被記錄在給定的紀錄檔案內。

#### get_clear_cases.py (結案土撥鼠)

指令格式：`python get_clear_cases.py [股別] [輸出檔名 (.txt)]`

支援輸入格式：不適用

**注意：若案件數規模與 2018 年嘉義分署的案件數規模不同，請特別注意是否須修改 `max_case_seqno` 變數。**

執行程式後會詢問使用者要查詢的案件種類、起始年分與截止年分。輸入後便開始查詢滿足如下條件的案件，並列出其中所有尚欠金額已為 0 的案件：

  - 指定股別
  - 執行年分從起始年分到截止年分間
  - 指定案件種類
  - 案號從 1 到 `max_case_seqno` 間

其中 `max_case_seqno` 為 `configs.py` 內的變數，預設為 `400000`。若往後有某類案件的案號超出此一數值，則須修正此變數令其大於當前的最大案號。

舉例而言，若股別指定為「愛」，案件種類填入 1，起始年分填入 106，截止年分填入 107，則程式會檢查 106 年與 107 年案號 1 到 `max_case_seqno` 的稅執案件，並將尚欠金額已為 0 的案件案號列印在輸出檔中。

若指定的案件種類為 4 (費執)，則程式會進一步詢問要查詢的案件是非勞保案件還是勞保案件，兩者不可混合。若查詢的標的為健保或是勞保，則程式會自動判斷是否連號已經全數尚欠金額皆為 0，符合者才會被視為可報結案件。

#### get_detainable_list.py (待扣存名單)

指令格式：`python get_detainable_list.py [股別] [輸出檔名 (.csv)]`

支援輸入格式：不適用

讀取指定股別之「金融存款餘額應扣未扣清單 (TPKI0602F)」頁面並存入輸出檔名，包含義務人統編、案件數、尚欠金額、金融餘額四個欄位，其中案件數與結案數計算方式同步，已對勞健保特別調整，故與案管系統上之數值不同。可用 Excel 篩選後搭配其他案管小工具使用。

#### get_VIP.py (大戶雷達儀)

指令格式：`python get_VIP.py [股別] [輸出檔名 (.txt)]`

支援輸入格式：不適用

**注意：若案件數規模與 2018 年嘉義分署的案件數規模不同，請特別注意是否須修改 `max_case_seqno` 變數。**

執行程式後會詢問使用者要尋找的標的是多案大戶還是高額大戶、案件數上下限與尚欠金額的上下限。輸入完畢後，程式會搜尋所有近五年內指定股別的義務人並計算每位義務人的案件數與尚欠金額，篩去兩者中有超出指定上下限者，再依照一開始指定的標的依案件數或尚欠金額排序，依序列印到輸出檔中。列印格式參照併卷小幫手以便於併卷辦案。

本程式與結案土撥鼠共用 `configs.py` 內的 `max_case_seqno` 變數，因此類似於結案土撥鼠，若往後有某類案件的案號超出 `max_case_seqno`，則須修正此變數令其大於當前的最大案號。

#### goodbye_cases.py (報結機器人)

指令格式：`python goodbye_cases.py [輸入檔名 (.csv)] [紀錄檔名 (.csv)]`

支援輸入格式：案號

**注意 1：若函稿編號與嘉義分署不同，終結情形包含憑證、退案、執行期限屆滿的案件將會因自動判斷失效而不被支援。**

**注意 2：在使用此程式前請務必確認 `configs.py` 內的 `default_dept` 變數是否已設定正確，否則所有案件皆會因權限不足查無資料而被誤判為案件已報結/掛結。**

本程式旨在實作電子憑證以外的案件的批次報結，並且內建自動判斷/檢查終結情形之機制。輸入檔內的每行應包含 4 欄，A~D 欄位的意義分別為 [年度] [類別] [案號首號] [案號末號]，其中案號末號僅需提供和首號不同的最後幾碼即可 (多亦無妨)。舉例而言，若使用者想要報結如下案件：

  1. 106 罰 123456 - 123458
  2. 105 稅 9998 - 10002
  3. 107 健 109990 - 110023
  4. 106 費 201782

則對應的 Excel 表格應為：

| | A | B | C | D |
| --- | --- | --- | --- | --- |
| 1 | 106 | 3 | 123456 | 8 |
| 2 | 105 | 1 | 9998 | 10002 |
| 3 | 107 | 2 | 109990 | 10023 |
| 4 | 106 | 4 | 201782 | |

程式會自動判斷案件之終結情形，故不須特別指定終結情形。若使用者想要手動指定終結情形，可於第 5 欄 (E 欄) 內輸入終結情形的代號，系統會自動判斷該終結情形是否合理，若不合理除該案件報結失敗外也會提示使用者系統自動判斷的可能終結情形。舉例而言，若上面的例子中，使用者想要指定 106 費 201782 為 01 完全繳清，則對應的表格為：

| | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- |
| 1 | 106 | 3 | 123456 | 8 | |
| 2 | 105 | 1 | 9998 | 10002 | |
| 3 | 107 | 2 | 109990 | 10023 | |
| 4 | 106 | 4 | 201782 | | 1 |

注意若輸入連號區間並指定終結情形，則此區間內所有案號都會以指定的終結情形報結，因此若連號中包含超過一種終結情形且欲逐一指定，必須拆開成多行報結。如 106 健 101234 - 101243，若 34 - 35 欲報 05、36 - 38 欲報 01、39 欲報 07、40 - 43 欲報 01，則應輸入 4 行如下：

| | A | B | C | D | E |
| --- | --- | --- | --- | --- | --- |
| 1 | 106 | 2 | 101234 | 5 | 5 |
| 2 | 106 | 2 | 101236 | 8 | 1 |
| 3 | 106 | 2 | 101239 | | 7 |
| 4 | 106 | 2 | 101240 | 3 | 1 |

少數情況下，自動判斷時案件的合理終結情形可能超過一種，則該案件將會報結失敗，並提示使用者系統判斷的所有可能終結情形，此時使用者便必須手動指定終結情形重新報結方可成功。

由於報結失敗的案件較多時，在螢幕上可能會不容易閱讀，故在輸出在螢幕上的同時，報結失敗案件的資訊也會同步列印到紀錄檔中。報結完後若發現並未全數成功，直接打開紀錄檔即可看見相關訊息；若所有案件都報結成功，輸出檔應為一空白的紀錄檔。

報結失敗的常見錯誤訊息如下：
  - 案件已報結/掛結
  - 無適當終結情形：自動判斷下未能發現任何合法終結情形。
  - 多重可能終結情形：自動判斷下發現一個以上的合法終結情形。
  - 終結情形不合法：除各項金額是否漏看外，也請注意辦案進行簿是否缺失命令紀錄，如：退案、憑證、屆期通知未有發文紀錄。

#### merge_helper.py (併卷小幫手)

指令格式：`python merge_helper.py [輸入檔名 (.csv)] [輸出檔名1 (.txt)] [輸出檔名 2 (.txt)](可選)`

支援輸入格式：案號、統編

本程式會將輸入檔內每個案號的其他未掛結案件表列顯示出來以方便併卷。執行後程式會詢問是否要顯示勞健保的案件與尚欠金額。

輸出檔名 1 是必要參數，執行後內容會是依照輸入檔順序的各義務人案件清單，案件依類別、年分、案號依序排序。若有提供輸出檔名 2，則內容會是輸出檔 1 中所有案件混合排序的結果，排序方式與輸出檔 1 相同。使用者可先依據輸出檔 2 的內容一口氣抽出架上的卷宗，再根據輸出檔 1 的內容從上個動作的卷堆中併卷。由於抽出後的卷堆依舊有序，併卷的步驟並不會太慢，但在抽卷階段卻可以省去大量的走動時間，從而加快併卷的速度。

輸出中有些案件後面會加上一些註記，目前註記可能有兩種：

  1. 如果是勞健保案件，則後面會加註星號 (*)。
  2. 如果是已經可結案 (尚欠金額為 0) 的案件，則後面會加註井號 (#)。

註：目前案管系統計算尚欠金額**非常**緩慢，若非必要**不建議**印出尚欠金額。

#### print_asset.py (自動印財冊)

指令格式：`python print_asset.py [輸入檔名 (.csv)] [紀錄檔名 (.csv)]`

支援輸入格式：案號、統編

自動列印輸入檔內清單上案件之義務人的財產清冊，若有多件義務人或獨資商號，則所有義務人/法定代理人與商號的資料皆會被查詢。程式開始執行後會根據輸入檔內的順序，以預設的列印選項依序列印財冊，兩件之間間隔時間為 `configs.py` 內設定的 `asset_wait_time` 變數決定，預設為 `5` 秒。

查詢及列印過程中若因為各種原因出錯，錯誤訊息會被記錄在給定的紀錄檔案內。

註：5 秒的時間包含打開已下載的財冊檔案與列印檔案所需的時間，因此時間若設定過短有可能未及列印便被中止程序，開始列印下一份財冊。若使用時發現有漏印情形，請至 `configs.py` 調整 `asset_wait_time` 變數直到錯誤不再發生。

#### print_bank_response.py (自動 508)

指令格式：`python print_bank_response.py [輸入檔名 (.csv)]`

支援輸入格式：案號、統編

自動列印輸入檔內清單上義務人最新的電子扣押存款金融機構回覆。程式開始執行後會根據輸入檔內的順序，以預設的列印選項依序列印金融機構回覆，兩件之間間隔時間為 `configs.py` 內設定的 `bank_wait_time` 變數決定，預設為 `5` 秒。

註：類似自動印財冊，若使用時發現有漏印情形，請至 `configs.py` 調整 `bank_wait_time` 變數直到錯誤不再發生。

#### range_list_gen.py (案號生成器)

指令格式：`python range_list_gen.py [輸出檔名 (.csv)] [股別] [年度] [案件類別] [區間起始號] [區間結束號]`

支援輸入格式：不適用

自動生成指定股別在 [年度] [案件類別] [區間啟始號] - [區間結束號] 區間內的案件。

#### regret_cases.py (反報機器人)

指令格式：`python regret_cases.py [輸入檔名 (.csv)] [紀錄檔名 (.csv)]`

支援輸入格式：案號

作為報結機器人的對偶，本程式提供批次反報結的功能。輸入檔的格式與報結機器人完全相同，若某些列的 E 欄因指定終結情形而有內容，本程式會忽略該欄位的內容，因此提交給報結機器人的輸入檔也完全相容於本程式。

類似於報結機器人，反報結失敗的資訊也會同步列印到紀錄檔中。

由於反報結本身的特性，反報結失敗幾乎只會有一種原因：案件並未處於已報結狀態。此時錯誤訊息應為「查無案件資料」。

### 檔案室相關功能

#### get_ended_case_list.py (年度歸檔冊)

指令格式：`python get_ended_case_list.py [輸出檔名 (.csv)]`

支援輸入格式：不適用

程式執行的一開始會詢問使用者欲查詢的年分。輸入後，程式會找出所有「檔號」(而非歸檔日期) 為指定年分的案件，並輸出至輸出檔中。

#### get_todestroy_stats.py (應銷統計表)

指令格式：`python get_todestroy_stats.py [輸入檔名 (.csv)] [輸出檔名 (.csv)]`

支援輸入格式：不適用

本程式會自動生成各股應銷毀案件清冊，以及應銷毀案件統計表。

此程式的輸入檔並非由使用者輸入生成，而是直接讀取年度歸檔冊的輸出檔案。使用者在透過年度歸檔冊獲得輸出檔後，將該輸出檔做為輸入檔執行此程式後，程式會詢問輸入檔的年分，以及欲銷毀應銷毀日期在何日以前的案件。使用者輸入後，程式會根據輸入的條件，將輸入檔內符合條件的案件依股別分類生成各股應銷毀案件清冊，並清查案件數製成應銷毀案件統計表。

本程式的輸出檔會有多個，包含兩類：

  1. 各股的應銷毀案件清冊。此類的輸出檔會有多份，一股一份，輸出檔名形如 `[輸入檔名前綴]_[股別].csv`。
  2. 應銷毀案件統計表。總共一份，輸出檔名即指定的輸出檔名。

### 統計室相關功能

#### print_daily_payment_list.py (Key 金額列表)

指令格式：`python print_daily_payment_list.py`

支援輸入格式：不適用

本程式執行後會詢問使用者欲查詢的日期，接著自動列印指定日期中，各股 Key 金額的案件列表，一股一份。

**注意：由於並非每股每天都會有 Key 金額的紀錄，若遇到某股無 Key 金額的紀錄時，案管會無法提供對應的 .pdf 檔，從而讓本程式出現「下載失敗」的錯誤訊息。**
