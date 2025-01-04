import Api from "@/api";

export default class Dns {
  static async getRecords() {
    return await Api.get('/dns');
  }

  static async addRecord(domain, ip) {
    return await Api.put('/dns', {
      domain,
      ip,
    })
  }

  static async deleteRecord(domain, ip) {
    return await Api.delete('/dns', {
      domain,
      ip,
    })
  }
}
