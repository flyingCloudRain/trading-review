# 清除 Streamlit 缓存

如果遇到数据库表结构错误，可能是 Streamlit 缓存了旧的表结构信息。

## 解决方法

### 方法1：重启 Streamlit 应用
```bash
# 停止当前运行的 Streamlit
# 然后重新启动
streamlit run streamlit_app.py
```

### 方法2：清除 Streamlit 缓存目录
```bash
# 删除 Streamlit 缓存
rm -rf ~/.streamlit/cache
```

### 方法3：在 Streamlit 界面清除缓存
1. 在 Streamlit 应用界面
2. 点击右上角的 "⋮" 菜单
3. 选择 "Clear cache"
4. 刷新页面

### 方法4：使用代码清除缓存
在 Streamlit 页面中添加清除缓存按钮：

```python
if st.button("清除缓存"):
    st.cache_data.clear()
    st.success("缓存已清除，请刷新页面")
```

## 验证表结构

运行以下命令验证表结构是否正确：

```bash
python3 verify_table_structure.py
```

如果表结构正确，但仍有错误，请重启 Streamlit 应用。

