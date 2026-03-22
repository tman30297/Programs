#!/usr/bin/env python3
"""
System Dashboard - Streamlit Web UI
Shows: CPU, Memory, Disk, Network, Services with start/stop/restart
"""

import streamlit as st
from streamlit_autorefresh import st_autorefresh
import psutil
import time
import socket
import os
import subprocess
from datetime import datetime

st.set_page_config(page_title="System Dashboard", page_icon="🖥️", layout="wide")

# Auto-refresh every 2 seconds for smooth live metrics
st_autorefresh(interval=2000, limit=None, key="metrics_refresh")

# Get local IP dynamically
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

# Service definitions
SERVICES = {
    "OpenClaw Gateway": {"port": 8080, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/"},
    "Ollama AI": {"port": 11434, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:11434/"},
    "Brain Web UI": {"port": 8080, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/"},
    "Brain Graph": {"port": 8080, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/graph.html"},
    "Brain Browser": {"port": 8080, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/browser.html"},
    "Brain API": {"port": 8081, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/"},
    "Research Topics": {"port": 8766, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8766/"},
    "Code Executor": {"port": 8767, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8767/"},
    "brain_all Search": {"port": 8768, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8768/brain_all_gui.html"},
    "System Dashboard": {"port": 8765, "check": "curl -s -o /dev/null -w '%{http_code}' http://localhost:8765/"},
}

def check_service(name):
    """Check if a service is running"""
    svc = SERVICES.get(name, {})
    port = svc.get("port")
    if port:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    return False

def get_service_actions():
    """Return dict of service status"""
    status = {}
    for name in SERVICES:
        status[name] = check_service(name)
    return status

def get_gpu_usage():
    """Get GPU usage and temp via nvidia-smi"""
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(",")
            util = int(parts[0].strip().replace(" %", ""))
            temp = int(parts[1].strip().replace(" C", "").replace("°C", ""))
            mem_used = int(parts[2].strip().replace(" MiB", ""))
            mem_total = int(parts[3].strip().replace(" MiB", ""))
            return {"available": True, "util": util, "temp": temp, "mem_used": mem_used, "mem_total": mem_total}
    except:
        pass
    return {"available": False}

def get_cpu_cores():
    """Get per-core CPU usage"""
    return psutil.cpu_percent(interval=0.5, percpu=True)

def get_disk2_info():
    """Get second disk (Drive2) info"""
    try:
        disk = psutil.disk_usage('/media/tony/Drive2')
        return {"available": True, "total": disk.total, "used": disk.used, "free": disk.free, "percent": disk.percent}
    except:
        return {"available": False}

def get_system_temps():
    """Get CPU, GPU, Memory temps from hwmon"""
    temps = {"cpu": None, "gpu": None, "memory": None, "ambient": None}
    try:
        # Read from dell_smm hwmon
        with open("/sys/class/hwmon/hwmon6/temp1_label", "r") as f:
            label = f.read().strip()
        with open("/sys/class/hwmon/hwmon6/temp1_input", "r") as f:
            val = int(f.read().strip()) / 1000
        if "CPU" in label:
            temps["cpu"] = val
        elif "SODIMM" in label or "Memory" in label:
            temps["memory"] = val
        elif "Ambient" in label:
            temps["ambient"] = val
        # Check all temp sensors in hwmon6
        for i in range(1, 10):
            try:
                label_file = f"/sys/class/hwmon/hwmon6/temp{i}_label"
                input_file = f"/sys/class/hwmon/hwmon6/temp{i}_input"
                if os.path.exists(label_file) and os.path.exists(input_file):
                    with open(label_file, "r") as f:
                        label = f.read().strip()
                    with open(input_file, "r") as f:
                        val = int(f.read().strip()) / 1000
                    if "CPU" in label:
                        temps["cpu"] = val
                    elif "SODIMM" in label or "Memory" in label:
                        temps["memory"] = val
                    elif "Ambient" in label:
                        temps["ambient"] = val
                    elif "GPU" in label:
                        temps["gpu"] = val
            except:
                pass
    except:
        pass
    # Get GPU temp from nvidia-smi as fallback
    if temps["gpu"] is None:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                temps["gpu"] = int(result.stdout.strip().replace(" C", "").replace("°C", ""))
        except:
            pass
    return temps

# Title
st.title("🖥️ System Dashboard")
st.markdown(f"**Host:** {socket.gethostname()} | **IP:** {LOCAL_IP} | **Uptime:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Temperature warning
temps = get_system_temps()
max_temp = 0
if temps.get("cpu"):
    max_temp = max(max_temp, temps["cpu"])
if temps.get("gpu"):
    max_temp = max(max_temp, temps["gpu"])
if max_temp >= 80:
    st.error(f"⚠️ WARNING: Temperature critical ({max_temp}°C) - Workload throttled!")
elif max_temp >= 70:
    st.warning(f"🌡️ Temperature elevated ({max_temp}°C) - Monitoring closely")
else:
    st.success(f"🌡️ Temperatures normal (CPU: {temps.get('cpu', 'N/A')}°C | GPU: {temps.get('gpu', 'N/A')}°C)")

# Metrics row (auto-refreshes every 2 seconds via st_autorefresh)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    cpu = psutil.cpu_percent(interval=0.5)
    st.metric("CPU", f"{cpu}%", delta_color="inverse")

with col2:
    gpu = get_gpu_usage()
    if gpu["available"]:
        st.metric("GPU", f"{gpu['util']}%", delta=f"{gpu['temp']}°C | {gpu['mem_used']}MB/{gpu['mem_total']}MB")
    else:
        st.metric("GPU", "N/A")

with col3:
    mem = psutil.virtual_memory()
    st.metric("Memory", f"{mem.percent}%", delta=f"{mem.used//(1024**3)}GB/{mem.total//(1024**3)}GB")

with col4:
    disk = psutil.disk_usage('/')
    st.metric("Disk (System)", f"{disk.percent}%", delta=f"{disk.free//(1024**3)}GB free")

with col5:
    net_io = psutil.net_io_counters()
    st.metric("Network", f"{net_io.bytes_recv/(1024**2):.1f}MB", f"{net_io.bytes_sent/(1024**2):.1f}MB sent")

# Detailed metrics row
st.subheader("📊 Detailed Metrics")

det_col1, det_col2, det_col3, det_col4 = st.columns(4)

with det_col1:
    st.markdown("**🖥️ CPU Cores**")
    cores = get_cpu_cores()
    for i, usage in enumerate(cores):
        st.progress(usage/100, text=f"Core {i}: {usage}%")

with det_col2:
    temps = get_system_temps()
    st.markdown("**🌡️ Temperatures**")
    if temps["cpu"]:
        st.metric("CPU", f"{temps['cpu']}°C")
    if temps["gpu"]:
        st.metric("GPU", f"{temps['gpu']}°C")
    if temps["memory"]:
        st.metric("Memory", f"{temps['memory']}°C")
    if temps["ambient"]:
        st.metric("Ambient", f"{temps['ambient']}°C")

with det_col3:
    st.markdown("**💾 Memory**")
    mem = psutil.virtual_memory()
    st.progress(mem.percent/100, text=f"Used: {mem.used//(1024**3)}GB / {mem.total//(1024**3)}GB")
    st.markdown(f"- **Available:** {mem.available//(1024**3)}GB")
    st.markdown(f"- **Cached:** {mem.cached//(1024**3)}GB")

with det_col4:
    st.markdown("**💽 Drive2 (Secondary)**")
    disk2 = get_disk2_info()
    if disk2["available"]:
        st.progress(disk2["percent"]/100, text=f"Used: {disk2['used']//(1024**3)}GB / {disk2['total']//(1024**3)}GB")
        st.markdown(f"- **Total:** {disk2['total']//(1024**3)}GB")
        st.markdown(f"- **Free:** {disk2['free']//(1024**3)}GB")
        st.markdown(f"- **Used:** {disk2['used']//(1024**3)}GB")
    else:
        st.markdown("Drive2 not available")

# Temperature row
st.subheader("🌡️ Temperatures")

temp_col1, temp_col2, temp_col3, temp_col4 = st.columns(4)

temps = get_system_temps()

with temp_col1:
    if temps["cpu"]:
        st.metric("CPU", f"{temps['cpu']}°C")
    else:
        st.metric("CPU", "N/A")

with temp_col2:
    if temps["gpu"]:
        st.metric("GPU", f"{temps['gpu']}°C")
    else:
        st.metric("GPU", "N/A")

with temp_col3:
    if temps["memory"]:
        st.metric("Memory", f"{temps['memory']}°C")
    else:
        st.metric("Memory", "N/A")

with temp_col4:
    if temps["ambient"]:
        st.metric("Ambient", f"{temps['ambient']}°C")
    else:
        st.metric("Ambient", "N/A")

st.divider()

# Service Manager
st.header("🔧 Service Manager")

# Refresh button
if st.button("🔄 Refresh Status"):
    st.rerun()

# Get current service status
service_status = get_service_actions()

# Service control columns
for name, running in service_status.items():
    colSvc1, colSvc2, colSvc3 = st.columns([2, 2, 1])
    with colSvc1:
        status_icon = "🟢" if running else "🔴"
        st.write(f"{status_icon} **{name}** (Port: {SERVICES[name]['port']})")
    with colSvc2:
        if running:
            st.success("Running")
        else:
            st.error("Stopped")
    with colSvc3:
        if name == "OpenClaw Gateway":
            if st.button(f"⏹️ Stop", key=f"stop_{name}", disabled=not running):
                subprocess.run(["openclaw", "gateway", "stop"], capture_output=True)
                time.sleep(2)
                st.rerun()
            if st.button(f"▶️ Start", key=f"start_{name}", disabled=running):
                subprocess.run(["openclaw", "gateway", "start"], capture_output=True)
                time.sleep(2)
                st.rerun()
            if st.button(f"🔄 Restart", key=f"restart_{name}"):
                subprocess.run(["openclaw", "gateway", "restart"], capture_output=True)
                time.sleep(3)
                st.rerun()

st.divider()

# System Info
colInfo1, colInfo2 = st.columns(2)

with colInfo1:
    st.subheader("💻 System Info")
    st.write(f"**Hostname:** {socket.gethostname()}")
    st.write(f"**OS:** {os.uname().sysname} {os.uname().release}")
    st.write(f"**Python:** {os.sys.version.split()[0]}")

with colInfo2:
    st.subheader("🔌 Network")
    addrs = psutil.net_if_addrs()
    for iface, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                st.write(f"**{iface}:** {addr.address}")

# Quick Links
st.divider()
st.subheader("🔗 Quick Links")
links_col1, links_col2, links_col3, links_col4 = st.columns(4)

with links_col1:
    st.markdown(f"- [Brain](http://{LOCAL_IP}:8080/)")
    st.markdown(f"- [Brain Graph](http://{LOCAL_IP}:8080/graph.html)")
    st.markdown(f"- [Brain Browser](http://{LOCAL_IP}:8080/browser.html)")

with links_col2:
    st.markdown(f"- [Brain API](http://{LOCAL_IP}:8081/)")
    st.markdown(f"- [Research Topics](http://{LOCAL_IP}:8766/)")
    st.markdown(f"- [Code Executor](http://{LOCAL_IP}:8767/)")
    st.markdown(f"- [brain_all Search](http://{LOCAL_IP}:8768/brain_all_gui.html)")

with links_col3:
    st.markdown(f"- [OpenClaw Gateway](http://{LOCAL_IP}:8080/)")
    st.markdown(f"- [Ollama](http://{LOCAL_IP}:11434/)")

with links_col4:
    st.markdown(f"- [System Dashboard](http://{LOCAL_IP}:8765/)")

st.divider()

# PDF Tools Section
st.header("📄 PDF Tools")

pdf_col1, pdf_col2 = st.columns([1, 2])

with pdf_col1:
    st.subheader("PDF to Text")
    pdf_input = st.text_input("PDF File Path", placeholder="/media/tony/Drive2/python3/book.pdf")
    output_input = st.text_input("Output Text File (optional)", placeholder="Leave empty for same dir")
    
    if st.button("Convert to Text"):
        if pdf_input:
            import subprocess
            cmd = ["python3", "/media/tony/Drive2/Programs/pdf_to_text/pdf_to_text.py", pdf_input]
            if output_input:
                cmd.append(output_input)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                st.success("Conversion complete!")
                st.code(result.stdout)
            else:
                st.error(f"Error: {result.stderr}")
        else:
            st.warning("Please enter a PDF file path")

with pdf_col2:
    st.subheader("How to Use")
    st.markdown("""
    **PDF to Text Converter**
    - Enter the full path to a PDF file
    - Optionally specify output filename
    - Click convert to extract text
    
    **Output:** Creates a .txt file in the same directory as the PDF
    
    **Example paths:**
    - `/media/tony/Drive2/python3/*.pdf`
    - `/media/tony/Drive2/Rust/*.pdf`
    """)

    st.divider()

    # PDF Summarizer
    st.subheader("🤖 PDF AI Summarizer")
    
    # Get available models
    import json
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True, text=True, timeout=5
        )
        models = json.loads(result.stdout).get('models', [])
        model_names = [m['name'] for m in models]
        if not model_names:
            model_names = ["qwen3:latest"]
    except:
        model_names = ["qwen3:latest"]
    
    sum_col1, sum_col2 = st.columns([1, 1])
    
    with sum_col1:
        sum_pdf_input = st.text_input("PDF File to Summarize", key="sum_pdf", placeholder="/media/tony/Drive2/python3/book.pdf")
        sum_model = st.selectbox("AI Model", model_names, index=0)
        save_brain = st.checkbox("💾 Save to Brain", value=True, help="Automatically save summary to Brain knowledge base")
    
    with sum_col2:
        if st.button("Generate Summary", key="btn_summarize"):
            if sum_pdf_input:
                with st.spinner("Extracting text and generating summary..."):
                    cmd = ["python3", "/media/tony/Drive2/Programs/pdf_to_text/pdf_summarize.py", sum_pdf_input, sum_model]
                    if save_brain:
                        cmd.append("--save-brain")
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True, text=True, timeout=300
                    )
                    if result.returncode == 0:
                        # Extract summary from output
                        output = result.stdout
                        if "📝 SUMMARY" in output:
                            summary_start = output.find("📝 SUMMARY") + len("📝 SUMMARY\n===============================================\n")
                            summary_end = output.find("===============================================\n", summary_start)
                            summary = output[summary_start:summary_end].strip()
                            st.success("Summary generated!")
                            # Check if saved to brain
                            if "Brain:" in output:
                                brain_line = [l for l in output.split('\n') if 'Brain:' in l]
                                if brain_line:
                                    st.info(brain_line[0].strip())
                            st.markdown(summary)
                        else:
                            st.code(result.stdout)
                    else:
                        st.error(f"Error: {result.stderr}")
            else:
                st.warning("Please enter a PDF file path")

    st.divider()

    # PDF Q&A
    st.subheader("💬 PDF Q&A")
    
    qa_col1, qa_col2 = st.columns([1, 1])
    
    with qa_col1:
        qa_pdf_input = st.text_input("PDF File", key="qa_pdf", placeholder="/media/tony/Drive2/python3/book.pdf")
        qa_question = st.text_input("Your Question", key="qa_question", placeholder="What is chapter 3 about?")
        qa_model = st.selectbox("AI Model", model_names, index=0, key="qa_model")
    
    with qa_col2:
        if st.button("Ask Question", key="btn_qa"):
            if qa_pdf_input and qa_question:
                with st.spinner("Loading PDF and generating answer..."):
                    result = subprocess.run(
                        ["python3", "/media/tony/Drive2/Programs/pdf_to_text/pdf_qa.py", qa_pdf_input, qa_question, qa_model],
                        capture_output=True, text=True, timeout=180
                    )
                    if result.returncode == 0:
                        output = result.stdout
                        if "❓ QUESTION:" in output:
                            answer_start = output.find("==============================================\n", output.find("❓ QUESTION:")) + len("==============================================\n")
                            answer_end = output.find("==============================================\n", answer_start)
                            answer = output[answer_start:answer_end].strip()
                            st.success("Answer:")
                            st.markdown(answer)
                        else:
                            st.code(result.stdout)
                    else:
                        st.error(f"Error: {result.stderr}")
            else:
                st.warning("Please enter PDF path and question")


