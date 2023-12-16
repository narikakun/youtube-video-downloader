from yt_dlp import YoutubeDL
import flet as ft
from os.path import expanduser
import json
import subprocess

def main(page: ft.Page):
    page.title = "YouTube動画ダウンロードソフト Created by narikakun"
    page.window_height = 250
    page.window_width = 800

    def close_dlg(e):
        err_dlg.open = False
        downloadButton.disabled = False
        progressBar.value = 100
        progressText.value = "エラーで終了しました。"
        page.update()

    err_dlg = ft.AlertDialog(
        title=ft.Text("エラー"),
        modal=True,
        content=ft.Text("エラーメッセージ"),
        actions=[
            ft.TextButton("閉じる", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def showError(errMsg):
        err_dlg.content = ft.Text(errMsg)
        page.dialog = err_dlg
        err_dlg.open = True
        page.update()

    def logHook(d):
        if d["status"] == "downloading":
            percent = (d["downloaded_bytes"] / (d["total_bytes"] or 0)) * 100
            progressBar.value = percent
            progressText.value = f"ダウンロード中... {d['_default_template']}"
            progressText.update()
            progressBar.update()
        elif d["status"] == "finished":
            progressBar.value = 100
            progressText.value = "ダウンロード完了"
        else:
            print(d)

    def getMetaData():
        try:
            with YoutubeDL() as ydl:
                res = ydl.extract_info(f"https://youtube.com/watch?v={videoUrl.value}", download=False)
                return res["id"]
        except:
            showError("メタデータ取得エラーが発生しました")

    def videoDownload(e):
        try:
            if videoUrl.value == "":
                showError("動画URLが入力されていません。")
                return
            downloadButton.disabled = True
            progressBar.value = None
            progressText.value = "ダウンロード開始処理中... "
            page.update()
            videoId = getMetaData()
            downloadFolder.value = folderPath + f"\\{videoId}\\"
            downloadFolder.update()
            with YoutubeDL({
                'progress_hooks': [logHook],
                'outtmpl': folderPath + '/%(id)s/video.mp4'
            }) as ydl:
                ydl.download(f"https://youtube.com/watch?v={videoUrl.value}")
                downloadButton.disabled = False
                page.update()
        except:
            showError("ビデオダウンロード中取得エラーが発生しました")

    def folderOpen(e):
        subprocess.Popen(["explorer", rf"{downloadFolder.value}"], shell=True)

    progressBar = ft.ProgressBar(width=page.window_width - 20, value=0)
    progressText = ft.Text(value="")
    videoUrl = ft.TextField(label="動画URL", value="", prefix_text="https://youtube.com/watch?v=", expand=True)
    downloadButton = ft.FilledButton(text="ダウンロード", on_click=videoDownload)
    folderPath = expanduser("~") + "\\Downloads"
    downloadFolder = ft.TextField(label="保存先", value=folderPath, expand=True, read_only=True)
    downloadFolderOpen = ft.FilledButton(text="フォルダーを開く", on_click=folderOpen)

    pageColumn = ft.Column(
        [
            ft.Row(
                [
                    videoUrl,
                    downloadButton
                ]
            ),
            progressBar,
            progressText,
            ft.Row(
                [
                    downloadFolder,
                    downloadFolderOpen
                ]
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        scroll=ft.ScrollMode.ALWAYS,
        height=page.window_height - 60
    )
    
    page.add(
        pageColumn
    )

    def page_resize(e):
        pageColumn.height = page.window_height - 60
        progressBar.width = page.window_width - 20
        page.update()

    page.on_resize = page_resize


ft.app(target=main)
