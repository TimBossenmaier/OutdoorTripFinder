import { Component, OnInit } from '@angular/core';
import {Router} from '@angular/router';
import {AccountService} from '../shared/account.service';

@Component({
  selector: 'tf-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.css']
})
export class LayoutComponent implements OnInit {

  constructor(
    private router: Router,
    private as: AccountService
  ) {
    if (this.as.userValue) {
      this.router.navigate(['/']);
    }
  }

  ngOnInit(): void {
  }

}
