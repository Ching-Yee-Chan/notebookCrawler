num_threads=1   # 先用1个线程登录，然后把生成的profile复制几次给其他的线程用
pdf_root="D:\文献"  # 每次跑PDF数量不能超过100条，这是notebook数量的上限

for i in $(seq 1 $num_threads); do
    port=$((9000 + i))
    # TODO: 换成Firefox的路径
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" \
        --remote-debugging-port=$port \
        --user-data-dir="C:\Users\fkzxy\workspace\notebookCrawler\AutomationProfile_$i" &
    sleep 1
done

python run.py --num_threads $num_threads --pdf_root $pdf_root --start_port 9001