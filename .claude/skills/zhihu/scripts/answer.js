const { log, randomSleep, validateParams } = require('./utils');
const ImageUploader = require('./image-uploader');

class AnswerPublisher {
  constructor(page) {
    this.page = page;
    this.imageUploader = new ImageUploader(page);
  }

  async publish(params) {
    try {
      validateParams(params, ['questionId', 'content']);
      
      const { questionId, content, localImageDir = null } = params;
      
      log('info', `开始回答问题: ${questionId}`);

      let processedContent = content;
      if (localImageDir || content.includes('![')) {
        processedContent = await this.imageUploader.processMarkdownImages(content, localImageDir);
      }

      const url = `https://www.zhihu.com/question/${questionId}`;
      await this.page.goto(url, { waitUntil: 'networkidle' });
      await this.page.waitForTimeout(3000);

      const answerButton = await this.page.$('button:has-text("写回答")');
      if (!answerButton) {
        throw new Error('未找到写回答按钮');
      }

      await answerButton.click();
      await this.page.waitForTimeout(2000);

      const editor = await this.page.$('.RichText-editor');
      if (!editor) {
        throw new Error('未找到编辑器');
      }

      await editor.click();
      await randomSleep(500, 1000);

      await this.page.evaluate((content) => {
        const editor = document.querySelector('.RichText-editor');
        if (editor) {
          editor.innerHTML = content;
          editor.dispatchEvent(new Event('input', { bubbles: true }));
        }
      }, processedContent);

      await randomSleep(1000, 2000);

      const submitButton = await this.page.$('button:has-text("提交回答")');
      if (!submitButton) {
        throw new Error('未找到提交按钮');
      }

      await submitButton.click();
      await this.page.waitForTimeout(3000);

      const currentUrl = this.page.url();
      if (currentUrl.includes('/answer/')) {
        log('info', `回答发布成功: ${currentUrl}`);
        return {
          success: true,
          url: currentUrl,
          questionId: questionId
        };
      } else {
        throw new Error('回答发布失败');
      }
    } catch (error) {
      log('error', `回答发布失败: ${error.message}`);
      throw error;
    }
  }
}

module.exports = AnswerPublisher;
