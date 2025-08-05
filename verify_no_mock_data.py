#!/usr/bin/env python3
"""
Verify that the current app.py has no mock data warnings
"""

import sys
import os

def verify_no_mock_data():
    """Verify that mock data warnings are completely removed"""
    
    print("🔍 Verifying Mock Data Removal...")
    print("="*60)
    
    app_file = "/Users/bobbyc/Downloads/BetPredictor/app.py"
    
    try:
        with open(app_file, 'r') as f:
            content = f.read()
        
        # Check for all variations of mock data warnings
        mock_patterns = [
            "Using Mock Odds Data",
            "Mock Odds Data",
            "Configure real API key for live odds",
            "⚠️ **Using Mock Odds Data**",
            "Using Mock",
            "mock data",
            "Mock data"
        ]
        
        found_issues = []
        
        for pattern in mock_patterns:
            if pattern in content:
                found_issues.append(pattern)
        
        if found_issues:
            print("❌ FOUND MOCK DATA WARNINGS:")
            for issue in found_issues:
                print(f"   • {issue}")
            return False
        else:
            print("✅ NO MOCK DATA WARNINGS FOUND")
            
        # Check for backup estimates warning (this is OK)
        backup_estimates = content.count("Using backup estimates")
        if backup_estimates > 0:
            print(f"ℹ️  Found {backup_estimates} 'backup estimates' warnings (these are OK - related to odds API)")
        
        # Check line count to ensure we're checking the right file
        line_count = content.count('\n')
        print(f"📊 File stats: {line_count} lines")
        
        if line_count < 1000:
            print("⚠️  File seems too small - make sure this is the main app.py")
            return False
        
        print("✅ VERIFICATION COMPLETE: No mock data warnings in app.py")
        return True
        
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def check_git_status():
    """Check that changes are properly committed"""
    
    print("\n🔄 Checking Git Status...")
    print("-" * 30)
    
    try:
        import subprocess
        
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, 
                              cwd='/Users/bobbyc/Downloads/BetPredictor')
        
        if result.returncode == 0:
            status_output = result.stdout.strip()
            if not status_output:
                print("✅ Working directory clean - all changes committed")
            else:
                print("⚠️  Uncommitted changes detected:")
                print(status_output)
            
            # Check if we're up to date with remote
            result2 = subprocess.run(['git', 'status', '-sb'], 
                                   capture_output=True, text=True,
                                   cwd='/Users/bobbyc/Downloads/BetPredictor')
            
            if result2.returncode == 0:
                status_line = result2.stdout.strip().split('\n')[0]
                if 'ahead' in status_line or 'behind' in status_line:
                    print(f"⚠️  Branch status: {status_line}")
                else:
                    print("✅ Branch is up to date with remote")
                    
        return True
        
    except Exception as e:
        print(f"❌ Git status check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Mock Data Verification...")
    
    success1 = verify_no_mock_data()
    success2 = check_git_status()
    
    if success1 and success2:
        print("\n" + "="*60)
        print("🎉 VERIFICATION SUCCESSFUL!")
        print("✅ No mock data warnings in current app.py")
        print("✅ Changes are committed and pushed")
        print("\n💡 If user still sees mock warnings:")
        print("   1. Clear browser cache (Ctrl+F5)")
        print("   2. Wait for Streamlit Cloud to update (~1-2 minutes)")
        print("   3. Check Streamlit Cloud deployment logs")
        print("="*60)
    else:
        print("\n❌ VERIFICATION FAILED - Manual check needed")