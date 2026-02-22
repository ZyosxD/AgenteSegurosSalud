## 2025-03-01 - Selenium Element Filtering
**Learning:** Filtering elements by ancestry (e.g., excluding header/nav) using `driver.execute_script` inside a Python loop is an N+1 performance killer in Selenium.
**Action:** Move filtering logic to the XPath query itself (e.g., `not(ancestor::header)`) to let the browser engine handle it in a single pass.
