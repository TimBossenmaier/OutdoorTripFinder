export class User {
  id?: string;
  username: string;
  email: string;
  password?: string;
  token?: string;
  approved?: boolean;
  confirmed?: boolean;
  role_id?: number;
  expiration_ts: string;

  constructor(username?, email?, role_id?) {
    this.username = username;
    this.email = email;
    this.role_id = role_id;
  }


}


