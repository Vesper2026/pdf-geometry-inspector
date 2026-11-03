# PDF 頁面幾何與中繼資料預檢

[English](README.md) · [網站](https://pdf.vesperai.space/zh-Hant/)

唯讀檢查本機 PDF 的頁面幾何與中繼資料：MediaBox、CropBox 交集、UserUnit 與四分之一圈旋轉。

## 執行

需要 Python 3.10+。clone 後在儲存庫根目錄操作：

```sh
git clone https://github.com/Vesper2026/pdf-geometry-inspector.git
cd pdf-geometry-inspector
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe examples/generate_sample.py
.venv/Scripts/python.exe pdf_geometry.py examples/sample.pdf --output examples/output
```

macOS／Linux 將 `.venv/Scripts/python.exe` 換成 `.venv/bin/python`。固定依賴見 requirements.txt；重新散布依賴時保留其 BSD-3-Clause 授權。

## 輸入與真實範例輸出

```text
Three synthetic blank pages: A4; rotated A4; Letter with CropBox [18,36,594,756].
```

隨附完整範例（不只是上面的縮寫說明）會產生：

```text
examples/output/inspection.json
examples/output/inspection.md
```

報告原始框、有效可見幾何、點／毫米、旋轉、方向、尺寸分組與中繼資料。Letter 裁切在 UserUnit 1 時可見範圍為 576 × 720 點，即 203.2 × 254 毫米。UserUnit 縮放座標尺寸；90／270 度旋轉互換寬高。裁切超出 MediaBox、非正矩形、空交集與不支援旋轉均提示人工覆核，不自動修復。受限加密文件不會產生虛構的頁面明細。

## 核心測試

```sh
.venv/Scripts/python.exe -m unittest discover -p "test_*.py"
```

測試驗證核心規則與合成範例，不驗證使用者文件的事實或翻譯品質。

## 限制與資料處理

唯讀幾何檢查不是渲染、OCR、修復、簽章驗證、安全遮蔽、來源認證或完整 PDF 合規檢查。混合尺寸可能是刻意安排。中繼資料可缺失或偽造。不破解密碼、不上傳文件。安裝 pypdf 會連接套件來源；pypdf 是 BSD-3-Clause 第三方依賴，不是私有產品程式碼。

## 本工具的獨立雙語站

```sh
python site/build.py
python -m http.server 8090 --directory docs
```

開啟 http://localhost:8090/zh-Hant/ 或 /en/。來源在 `site/`，輸出在 `docs/`，範例複製到 `docs/downloads/`。每種語言有兩篇原創文章，以及獨立 hostname、canonical、sitemap、robots 與 CNAME；沒有追蹤分析或上傳表單。Pages 來源為 main:/docs。靜態資源由 GitHub 託管，外部連結仍會連接各自服務。

## 相關產品與維護關係

[KomoPDF](https://komopdf.com/) 是相關產品，不是本工具的依賴。KolmoPDF 雲端服務會上傳文件，本機開源 CLI 不取代其專有解析器。

由 Vesper2026 維護，與相關的 Eqvero、KolmoPDF、KomoPDF 生態屬同一維護團隊。不是獨立第三方背書，也不是產品私有實作。

## 授權

自有程式、合成資料、文件與靜態站來源採 MIT，見 LICENSE；第三方依賴保留原授權。
