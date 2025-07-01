#!/bin/bash
# Package Lambda functions with dependencies

echo "🚀 Packaging Lambda functions with dependencies..."

# Create temporary directories
mkdir -p ci-package alert-package

# Package CI Orchestration Lambda
echo "📦 Packaging CI Orchestration Lambda..."
cp ci_orchestration_function.py ci-package/
pip install -r requirements.txt -t ci-package/ --platform manylinux2014_x86_64 --only-binary=:all:
cd ci-package && zip -r ../ci-orchestration-full.zip . && cd ..
echo "✅ CI Orchestration package ready!"

# Package Alert Orchestration Lambda  
echo "📦 Packaging Alert Orchestration Lambda..."
cp alert_orchestration_function.py alert-package/
pip install -r requirements.txt -t alert-package/ --platform manylinux2014_x86_64 --only-binary=:all:
cd alert-package && zip -r ../alert-orchestration-full.zip . && cd ..
echo "✅ Alert Orchestration package ready!"

# Cleanup
rm -rf ci-package alert-package

echo "🎉 Both Lambda packages ready for deployment!"