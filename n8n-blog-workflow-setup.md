# n8n Blog Workflow Setup Guide

Complete instructions for importing and configuring the automated blog publishing workflow for MurmurTone.

## Prerequisites

- Access to n8n instance at https://n8n.tuckercorp.org
- GitHub credential configured in n8n (ID: `Yc0tIZxQTaV6u8Ms`)
- OpenAI credential configured in n8n (ID: `Y9V7ZtGMXYd5M6Ky`)
- Slack credential configured in n8n (ID: `Hn7aAZDO8tem9skO`)

## Import Workflow

### Step 1: Open n8n

1. Navigate to https://n8n.tuckercorp.org
2. Log in with your credentials

### Step 2: Import Workflow JSON

1. Click **Workflows** in the left sidebar
2. Click the **+** button or **Add Workflow**
3. Click the **⋮** (three dots menu) in the top right
4. Select **Import from File**
5. Choose the file: `murmurtone-blog-workflow.json`
6. Click **Import**

### Step 3: Verify Credentials

After import, verify all credentials are properly connected:

1. Click on each HTTP Request node with credentials:
   - **Generate Topic with OpenAI** → Should show "OpenAI Header Auth"
   - **Generate Article with OpenAI** → Should show "OpenAI Header Auth"
   - **Get Latest Commit SHA** → Should show "RV GitHub Header Auth"
   - **Create All Blobs** → Should show "RV GitHub Header Auth"
   - **Get Base Tree SHA** → Should show "RV GitHub Header Auth"
   - **Create Tree** → Should show "RV GitHub Header Auth"
   - **Create Commit** → Should show "RV GitHub Header Auth"
   - **Update Master Ref** → Should show "RV GitHub Header Auth"
   - **Send Slack Notification** → Should show "Slack OAuth"

2. If any credential is missing, click the node and select the correct credential from the dropdown

### Step 4: Save Workflow

1. Click **Save** in the top right
2. Workflow name should be: **MurmurTone - Automated Blog Publishing**

## Test Workflow

Before activating the schedule, test the workflow manually.

### Manual Test Run

1. Click **Execute Workflow** button (or press Ctrl+Enter)
2. Watch the workflow execution:
   - All nodes should turn green (success)
   - If any node turns red, click it to see the error
3. Check the results:
   - Click **Send Slack Notification** node to see the message sent
   - Verify GitHub commit was created
   - Check https://murmurtone.com/blog.html for new post

### Verify Deployment

1. Wait 2-3 minutes for Cloudflare Pages to deploy
2. Visit the new blog post URL (shown in Slack message)
3. Verify:
   - Post loads correctly with all styling
   - Navigation works
   - RSS feed at https://murmurtone.com/feed.xml includes the post
   - Sitemap at https://murmurtone.com/sitemap.xml includes the post

### Test Again (Second Post)

1. Execute workflow again manually
2. Verify no duplicate topics (check blog-state.json has 2 different posts)
3. Confirm blog.html shows both posts
4. Check feed.xml has 2 items

## Activate Schedule

Once testing is successful:

### Step 1: Enable Schedule Trigger

1. Click the **Schedule Every 3 Days** node
2. Verify cron expression: `0 10 */3 * *` (every 3 days at 10:00 AM UTC)
3. No changes needed - already configured

### Step 2: Activate Workflow

1. Click the toggle switch in the top right to **Active**
2. Status should change from "Inactive" to "Active"

### Step 3: Verify Next Execution

1. In the workflow list, find "MurmurTone - Automated Blog Publishing"
2. Check the **Next Execution** column
3. Should show date/time 3 days from last execution

## Monitoring

### Check Execution History

1. Click **Executions** in left sidebar
2. Filter by workflow: "MurmurTone - Automated Blog Publishing"
3. Click any execution to see details:
   - Green = success
   - Red = failed
   - Click nodes to see input/output data

### Slack Notifications

All executions send Slack notifications to **#new-tickets** channel:

**Success message includes:**
- Post title and URL
- Word count and read time
- Target keywords
- GitHub commit URL
- Pre-written tweet text

**Failure handling:**
- If workflow fails, Slack will receive error notification
- Check n8n execution history for details

## Troubleshooting

### Common Issues

**Issue: "Permission Denied" on GitHub API**
- **Cause**: GitHub credential expired or incorrect
- **Fix**: Update GitHub credential in n8n settings with new token

**Issue: OpenAI rate limit exceeded**
- **Cause**: Too many API calls
- **Fix**: Wait 1 minute and retry, or check OpenAI account quota

**Issue: Duplicate topics generated**
- **Cause**: blog-state.json not updated correctly
- **Fix**: Manually edit blog-state.json to include all previous titles

**Issue: Slack notification fails but blog publishes**
- **Cause**: Slack credential issue (non-critical)
- **Fix**: Check Slack OAuth token, refresh if needed
- **Note**: Blog will still publish successfully

**Issue: Cloudflare deployment doesn't trigger**
- **Cause**: GitHub commit may have failed
- **Fix**: Check GitHub repo commits, verify workflow reached "Update Master Ref" node

### Debug Mode

Enable debug mode to see detailed node outputs:

1. Click **Settings** (gear icon) in workflow
2. Enable **Save Execution Progress**
3. Enable **Save Manual Executions**
4. Click **Save**

Now you can click each node during/after execution to see:
- Input data
- Output data
- Error messages

## Schedule Details

- **Frequency**: Every 3 days at 10:00 AM UTC
- **Cron**: `0 10 */3 * *`
- **Expected posts**: ~10 per month
- **First execution**: 3 days after activation

### Converting UTC to Your Timezone

10:00 AM UTC is:
- 5:00 AM EST (UTC-5)
- 6:00 AM EDT (UTC-4)
- 2:00 AM PST (UTC-8)
- 3:00 AM PDT (UTC-7)

To change execution time, edit the cron expression in **Schedule Every 3 Days** node.

## Post-Deployment Setup

### Set Up dlvr.it for Auto-Tweeting

1. Go to https://dlvr.it
2. Sign up or log in
3. Add source: https://murmurtone.com/feed.xml
4. Connect Twitter account: @MurmurTone
5. Set route to post new items automatically
6. Verify first auto-tweet appears after next blog post

### Monitor First Month

Week 1:
- Check daily that executions succeed
- Verify posts publish correctly
- Monitor Twitter engagement

Weeks 2-4:
- Check weekly
- Review content quality
- Adjust OpenAI prompts if needed (topic/article generation nodes)

## Updating Prompts

### Topic Generation Prompt

To adjust topic generation, edit the **Build Topic Prompt** node:

1. Click the node
2. Edit the `systemPrompt` in the JavaScript code
3. Modify brand voice, target keywords, or messaging pillars
4. Click **Save**

### Article Generation Prompt

To adjust article writing, edit the **Build Article Prompt** node:

1. Click the node
2. Edit the `systemPrompt` in the JavaScript code
3. Modify structure, length, or tone requirements
4. Click **Save**

## Cost Tracking

Monitor OpenAI costs at https://platform.openai.com/usage

Expected monthly cost:
- Topic generation: ~500 tokens × 10 posts = 5,000 tokens
- Article generation: ~3,000 tokens × 10 posts = 30,000 tokens
- **Total**: ~35,000 tokens/month ≈ **$0.30/month** with GPT-4o

## Workflow Architecture

```
Schedule (every 3 days)
  ↓
Fetch blog-state.json
  ↓
Parse or Initialize State
  ↓
Build Topic Prompt
  ↓
Generate Topic with OpenAI
  ↓
Validate Topic
  ↓
Build Article Prompt
  ↓
Generate Article with OpenAI
  ↓
Calculate Metadata
  ↓
Fetch Template
  ↓
Build Post HTML
  ↓
Update State
  ↓
Regenerate blog.html
  ↓
Fetch blog.html Template
  ↓
Update blog.html
  ↓
Generate feed.xml
  ↓
Fetch sitemap.xml
  ↓
Update sitemap.xml
  ↓
Get Latest Commit SHA (GitHub)
  ↓
Prepare All Blobs
  ↓
Create All Blobs (5 files)
  ↓
Collect Blob SHAs
  ↓
Get Base Tree SHA
  ↓
Create Tree
  ↓
Create Commit
  ↓
Update Master Ref
  ↓
Prepare Slack Message
  ↓
Send Slack Notification
```

## Support

For issues with:
- **n8n workflow**: Check execution history, review error messages
- **GitHub commits**: Verify credential and check GitHub API rate limits
- **OpenAI generation**: Check API quota at platform.openai.com
- **Cloudflare deployment**: Check Cloudflare Pages dashboard
- **RSS/dlvr.it**: Verify feed.xml is valid at https://validator.w3.org/feed/

---

Last updated: 2026-01-25
