# 小米运动助手 (MiMotion Assistant)

一个基于 Flask 的小米运动（Zepp Life）自动刷步数工具，提供友好的 Web 界面和丰富的功能。

![小米运动助手](https://img.shields.io/badge/小米运动助手-v1.0-blue)
![Flask](https://img.shields.io/badge/Flask-v2.2.5-green)
![Python](https://img.shields.io/badge/Python-v3.6+-orange)

## 功能特点

- 🌟 **美观的 Web 界面**：基于 TailwindCSS 构建的现代化界面
- 👥 **多账号管理**：支持添加多个小米运动账号，统一管理和监控
- ⏰ **智能时间控制**：设置同步时间范围，根据时间自动计算合理的步数
- 📊 **数据可视化**：提供步数趋势图表和同步成功率统计分析
- 🔄 **自动定时同步**：按计划自动同步步数，无需手动操作
- 📱 **响应式设计**：在各种设备上都能良好显示

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/mimotion.git
cd mimotion
```

### 2. 创建虚拟环境

```bash
# 使用 conda 创建虚拟环境
conda create -n mimotion python=3.8
conda activate mimotion

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python update_db.py
```

### 5. 启动应用

```bash
python run.py
```

访问 http://127.0.0.1:5002 即可使用。

## 使用方法

1. **注册/登录**：首次使用需要注册账号，已有账号直接登录
2. **添加小米账号**：在"账号管理"页面添加小米运动账号
3. **设置参数**：
   - 设置步数范围（最小步数和最大步数）
   - 设置同步时间范围（开始时间和结束时间）
4. **查看统计**：在账号详情页查看同步记录和统计图表
5. **手动同步**：点击"同步"按钮可立即执行同步操作

## 项目结构

```
mimotion/
├── app/                    # 应用主目录
│   ├── controllers/        # 控制器
│   ├── models/             # 数据模型
│   ├── scheduler/          # 定时任务
│   ├── static/             # 静态资源
│   ├── templates/          # 模板文件
│   ├── utils/              # 工具函数
│   └── __init__.py         # 应用初始化
├── instance/               # 实例配置
├── run.py                  # 启动脚本
├── update_db.py            # 数据库更新脚本
└── requirements.txt        # 依赖列表
```

## 技术栈

- **后端**：Flask、SQLAlchemy、APScheduler
- **前端**：TailwindCSS、Font Awesome、ECharts
- **数据库**：SQLite

## 注意事项

1. 本项目仅供学习交流使用，请勿用于商业用途
2. 请合理设置步数范围，避免设置不合理的步数
3. 请遵守小米运动的使用条款
4. 账号密码等敏感信息存储在本地数据库，请确保安全

## 开源许可

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 致谢

本项目基于以下开源项目开发：

- [TonyJiangWJ/mimotion](https://github.com/TonyJiangWJ/mimotion) - 提供了小米运动刷步数的核心算法
- [Flask](https://flask.palletsprojects.com/) - Python Web 框架
- [TailwindCSS](https://tailwindcss.com/) - CSS 框架
- [ECharts](https://echarts.apache.org/) - 数据可视化图表库

---

如有问题或建议，欢迎提交 Issue 或 Pull Request。
