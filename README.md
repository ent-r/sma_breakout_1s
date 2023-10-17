# sma_breakout_1s
SMA calculation, 1-second breakout detection from WebSocket to FTP, with RAM-based database.

This algorithm is designed for real-time (1s) analysis of currency pairs in the Binance market. It utilizes WebSockets, FTP for file transfer, and operates with a RAM database to compute Simple Moving Averages (SMAs) and identify breakouts.

By integrating WebSockets, the algorithm acquires the most recent market data in real-time (1s), enabling rapid responses to market fluctuations and the identification of promising trading opportunities.

Using the FTP protocol, the system securely accesses historical datasets and combines them with real-time (1s) data to provide a comprehensive analysis of market trends.

The algorithm employs SMAs to assess the historical performance of currency pairs, predict future trends based on past price movements, and detect potential breakouts.

All these operations are executed in Python, utilizing the RAM as both a workspace and a database, with permanent backups to disk.
