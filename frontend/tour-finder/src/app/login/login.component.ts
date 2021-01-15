import { Component, OnInit } from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {AccountService} from '../shared/account.service';
import {AlertService} from '../shared/alert.service';
import {first} from 'rxjs/operators';

@Component({
  selector: 'tf-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  form: FormGroup;
  loading = false;
  submitted = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private as: AccountService,
    private als: AlertService
  ) { }

  ngOnInit(): void {
    this.form = this.fb.group(
      {
        username: ['', Validators.required],
        password: ['', Validators.required]
      }
    );
  }

  get f() { return this.form.controls; }

  onSubmit(){
    this.submitted = true;

    // reset alerts on submit
    this.als.clear();

    if (this.form.invalid) {
      return ;
    }

    this.loading = true;
    this.as.login(this.f.username.value, this.f.password.value)
      .pipe(first())
      .subscribe({
        next: () => {
          const returnUrl = this.route.snapshot.queryParams.returnUrl || '/';
          this.router.navigateByUrl(returnUrl);
        },
        error: err => {
          this.als.error(err);
          this.loading = false;
      }
      });
  }



}
