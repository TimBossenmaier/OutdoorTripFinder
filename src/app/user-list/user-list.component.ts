import { Component, OnInit } from '@angular/core';
import {AccountService} from '../shared/account.service';
import {first} from 'rxjs/operators';

@Component({
  selector: 'tf-user-list',
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.css']
})
export class UserListComponent implements OnInit {
  users = null;

  constructor(
    private as: AccountService
  ) { }

  ngOnInit(): void {
    this.as.getAll()
      .pipe(first())
      .subscribe(users => this.users = users);
  }

}
