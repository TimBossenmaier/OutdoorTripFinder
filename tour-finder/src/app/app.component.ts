import { Component } from '@angular/core';
import {User} from './shared/user';
import {AccountService} from './shared/account.service';

@Component({
  selector: 'tf-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'tour-finder';
  user: User;

  constructor(
    private as: AccountService
  ) {
    this.as.user.subscribe(x => this.user = x);
  }

  logout() {
    this.as.logout();
  }
}
