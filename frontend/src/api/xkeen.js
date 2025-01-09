import Api from "@/api/index.js";

export default class XKeen {
  static async getFile(filename) {
    return await Api.get(`/files/${filename}`);
  }

  static async writeFile(filename, content) {
    return await Api.put(`/files/${filename}`, {
      content,
    });
  }

  static async getStatus() {
    return await Api.get(`/xkeen/status`);
  }

  static async start() {
    return await Api.post(`/xkeen/start`);
  }

  static async restart() {
    return await Api.post(`/xkeen/restart`);
  }

  static async stop() {
    return await Api.post(`/xkeen/stop`);
  }
}
