# Quick Start Guide for Windows Users

Get started with Commerzbank FinTS Payout Automator in 3 simple steps.

## 🚀 Option 1: Download Pre-Built Executable (Recommended)

### Step 1: Download

1. Go to the [Releases](https://github.com/CJ-1981/commerzbank-fints/releases) page
2. Download the latest version: `CommerzbankFinTS_Payout_Automator-Windows-vX.X.X.zip`
3. Extract the ZIP file to any folder on your computer

### Step 2: Run

Double-click `CommerzbankFinTS_Payout_Automator.exe` to launch the application

### Step 3: Use

Enter your Commerzbank online banking credentials and start automating your SEPA transfers!

---

## 🛠️ Option 2: Build from Source

For advanced users who want to build from source code.

### Prerequisites

- Windows 10 or 11 (64-bit)
- Python 3.11 or higher

### Installation Steps

```powershell
# 1. Download the source code
git clone https://github.com/CJ-1981/commerzbank-fints.git
cd commerzbank-fints

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run the application
python commerzbank_fints_qt_desktop_app.py
```

---

## 📋 System Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Display**: 1024x768 minimum resolution
- **Network**: Stable internet connection required
- **Banking**: Commerzbank online banking with photoTAN access

---

## 🔐 Security Information

### What We Need

- **Commerzbank Online Banking Credentials** - For authentication
- **photoTAN Device** - For transaction authorization

### What We Store

- **Nothing** - Your PIN is never stored
- **No Credentials** - Fresh authentication each session
- **No Persistence** - All data is cleared when you close the application

### Connection Security

- **Encrypted** - SSL/TLS protected communication
- **Direct** - Connection goes only to Commerzbank servers
- **Secure** - Industry-standard FinTS/HBCI protocol

---

## ⚡ First-Time Setup

### 1. Launch the Application

Double-click the executable to start

### 2. Enter Your Banking Credentials

You'll need:
- **Bank Code (BLZ)**: Your Commerzbank bank code
- **User ID**: Your online banking username
- **PIN**: Your online banking PIN

### 3. Verify Connection

The application will retrieve your account information from Commerzbank

### 4. Configure Your Preferences

Set up default transfer settings and payout preferences

---

## 💡 Quick Usage Guide

### Creating a Batch Transfer

1. **Add Recipients**
   - Enter recipient name
   - Enter IBAN (auto-validated)
   - Enter amount in EUR
   - Enter payment reference/purpose

2. **Choose Transfer Strategy**
   - **Collective Batch**: All transfers in one photoTAN
   - **Individual Transfers**: Separate photoTAN for each

3. **Execute**
   - Click "Start Batch Execution"
   - Respond to photoTAN prompts on your smartphone
   - Monitor progress in real-time

4. **Track Results**
   - Watch the terminal log for status updates
   - Successful transfers show in green
   - Failed transfers show in red with error details

---

## 🛡️ Best Practices

### Before You Start

✅ **Verify Recipients** - Double-check IBANs and amounts
✅ **Test Small Amounts** - Start with small transfers to verify setup
✅ **Keep PhotoTAN Ready** - Ensure your smartphone is available
✅ **Stable Connection** - Use reliable internet connection

### During Execution

✅ **Watch the Log** - Monitor real-time status updates
✅ **Respond Quickly** - photoTAN challenges timeout after several minutes
✅ **Don't Close** - Keep the application open during execution
✅ **Save State** - Consider saving batch configuration for reuse

### After Completion

✅ **Verify Transactions** - Check your online banking for confirmation
✅ **Review Log** - Ensure all transfers succeeded
✅ **Close Securely** - Exit the application when done

---

## ❓ Troubleshooting

### Application Won't Start

**Solution**:
1. Ensure you're using Windows 10/11 64-bit
2. Check if antivirus is blocking the executable
3. Try running as administrator
4. Download a fresh copy from releases page

### Connection Errors

**Solution**:
1. Verify your internet connection
2. Check Commerzbank online banking is accessible
3. Verify your credentials are correct
4. Ensure photoTAN is properly configured

### photoTAN Issues

**Solution**:
1. Ensure your smartphone has internet connection
2. Check the Commerzbank photoTAN app is working
3. Respond to challenges promptly (they timeout)
4. Make sure you're using the correct photoTAN procedure

### Transfer Failures

**Solution**:
1. Verify recipient IBANs are correct
2. Check your account has sufficient funds
3. Ensure payment reference follows required format
4. Review error messages in the terminal log

---

## 📞 Getting Help

### Documentation

- [Full README](README.md) - Complete feature documentation
- [Build Guide](BUILD_GUIDE.md) - Building from source
- [Test Guide](TEST_EXECUTION_GUIDE.md) - Testing information

### Support

- **GitHub Issues**: [Report bugs](https://github.com/CJ-1981/commerzbank-fints/issues)
- **Documentation**: Check existing issues first
- **Community**: Share experiences and solutions

---

## ⚠️ Important Disclaimers

### Financial Responsibility

- **Verify All Transactions** - Always double-check amounts and recipients
- **Check Official Records** - Verify transfers in your official banking channel
- **Use at Own Risk** - This is a community-developed automation tool
- **No Warranty** - Software provided as-is without guarantees

### Security Best Practices

- **Secure Environment** - Use on secure, trusted computers only
- **Strong PIN** - Use a strong, unique PIN for online banking
- **Monitor Account** - Regularly check your bank statements
- **Report Issues** - Report security concerns promptly

---

## 🎯 Next Steps

1. **Download** the latest executable from releases
2. **Read** the full README for detailed features
3. **Test** with small amounts first
4. **Provide Feedback** - Report issues or suggest improvements

---

**Ready to automate your banking workflows?** 

[Download Latest Release](https://github.com/CJ-1981/commerzbank-fints/releases/latest)

---

**Made with ❤️ for efficient banking automation**
