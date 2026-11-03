const fs = require('node:fs');

/** Capture the owned Electron window, including hidden Windows compositor surfaces. */
async function captureWindow(app, filename) {
  let timer;
  try {
    const encoded = await Promise.race([
      app.evaluate(async ({ BrowserWindow }) => {
        const contents = BrowserWindow.getAllWindows()[0].webContents;
        const options = { stayHidden: true, stayAwake: true };
        // The first capture wakes a hidden surface but can contain its previous
        // frame. Wait for the requested scroll/layout to paint before saving.
        await contents.capturePage(undefined, options);
        await contents.executeJavaScript(
          'new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))',
        );
        return (await contents.capturePage(undefined, options)).toPNG().toString('base64');
      }),
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error('Electron capture timed out')), 15000);
      }),
    ]);
    if (!encoded) throw new Error('Electron returned an empty screenshot');
    fs.writeFileSync(filename, Buffer.from(encoded, 'base64'));
  } finally {
    clearTimeout(timer);
  }
}

module.exports = { captureWindow };
