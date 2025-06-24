# Standard Operating Procedures (SOPs)
## Cost-Effective Development Without Claude Code

### SOP: Adding New Book Category
**Estimated Time**: 15 minutes  
**Complexity**: Low  
**Prerequisites**: Local Python environment

#### Steps:
1. **Update market_scout.py categories list**
   ```python
   SUPPORTED_CATEGORIES = [
       "existing_category",
       "new_category_name"  # Add here
   ]
   ```

2. **Add validation in series_publisher.py**
   ```python
   def validate_category(category):
       if category not in SUPPORTED_CATEGORIES:
           raise ValueError(f"Unsupported category: {category}")
   ```

3. **Test locally with pytest**
   ```bash
   pytest tests/test_categories.py -v
   ```

4. **Deploy via GitHub Actions**
   ```bash
   git add . && git commit -m "feat: add new book category" && git push
   ```

---

### SOP: Hardcover Production for New Volume
**Estimated Time**: 10 minutes  
**Complexity**: Low  
**Prerequisites**: Existing paperback PDF

#### Steps:
1. **Copy configuration template**
   ```bash
   cp templates/hardcover/production_docs/book_config_template.json books/active_production/SERIES/volume_X/hardcover_config.json
   ```

2. **Update configuration**
   - title, subtitle, volume number
   - cover_source path
   - page count
   - pricing strategy

3. **Run automated production**
   ```bash
   python scripts/hardcover/create_hardcover_package.py books/active_production/SERIES/volume_X/hardcover_config.json
   ```

4. **Convert manuscript**
   ```bash
   python scripts/hardcover/convert_paperback_to_hardcover.py SOURCE.pdf TARGET.pdf
   ```

5. **Commit results**
   ```bash
   git add books/active_production/SERIES/volume_X/hardcover/
   git commit -m "feat: complete hardcover production for TITLE Volume X"
   git push
   ```

---

### SOP: GitHub Actions Workflow Debugging
**Estimated Time**: 20 minutes  
**Complexity**: Medium  
**Prerequisites**: GitHub access

#### Steps:
1. **Check workflow status**
   - Navigate to Actions tab
   - Identify failing workflow
   - Review error logs

2. **Local reproduction**
   ```bash
   # Install act for local testing
   brew install act
   act -j job_name
   ```

3. **Common fixes**
   - Missing dependencies: Update requirements.txt
   - Path issues: Use absolute paths
   - Environment variables: Check secrets

4. **Test and deploy**
   ```bash
   git add .github/workflows/
   git commit -m "fix: resolve workflow issue"
   git push
   ```

---

### SOP: AWS Lambda Deployment
**Estimated Time**: 5 minutes  
**Complexity**: Low  
**Prerequisites**: AWS credentials configured

#### Steps:
1. **Run deployment script**
   ```bash
   python scripts/utilities/deploy_lambda.py
   ```

2. **Verify deployment**
   ```bash
   aws lambda list-functions --query 'Functions[?FunctionName==`kindlemint-engine`]'
   ```

3. **Test function**
   ```bash
   aws lambda invoke --function-name kindlemint-engine --payload '{}' response.json
   ```

---

### SOP: Book Quality Validation
**Estimated Time**: 10 minutes  
**Complexity**: Low  
**Prerequisites**: PDF file exists

#### Manual Workflow:
1. **Run QA checker**
   ```bash
   python scripts/enhanced_qa_checker.py path/to/book.pdf
   ```

2. **Review output**
   - Font embedding status
   - Page count validation  
   - File size compliance
   - Print quality metrics

3. **Fix issues if found**
   - Re-export PDF with embedded fonts
   - Optimize file size if over limits
   - Verify page dimensions

#### Automated via GitHub Actions:
- Triggers automatically on PDF commits
- Results visible in Actions tab
- Blocks publication if quality fails

---

### Cost Optimization Checklist

#### Before Opening Claude Code:
- [ ] **Plan completely** in Claude Chat (free)
- [ ] **Write requirements** in detail
- [ ] **Batch similar tasks** together
- [ ] **Estimate complexity** and time needed

#### During Claude Code Session:
- [ ] **Use templates** whenever possible
- [ ] **Leverage prompt caching** with similar requests
- [ ] **Focus on single task type** per session
- [ ] **Track metrics**: lines changed, files modified

#### After Claude Code Session:
- [ ] **Log usage** with cost tracker
- [ ] **Commit all changes** immediately
- [ ] **Update SOPs** if new patterns emerge
- [ ] **Plan next session** if needed

#### Weekly Review:
- [ ] **Run usage report** to identify expensive patterns
- [ ] **Review SOPs** for optimization opportunities
- [ ] **Update templates** with frequently used code
- [ ] **Plan batch sessions** for upcoming work