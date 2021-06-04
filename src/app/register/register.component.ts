import { Component, OnInit } from '@angular/core';
import {FormBuilder, FormGroup, Validators} from '@angular/forms';
import {ActivatedRoute, Router} from '@angular/router';
import {AccountService} from '../shared/account.service';
import {AlertService} from '../shared/alert.service';
import {first} from 'rxjs/operators';

@Component({
  selector: 'tf-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
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
    this.form = this.fb.group({
      username: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  get f() { return this.form.controls; }

  onSubmit() {
    this.submitted = true;

    this.als.clear();

    if (this.form.invalid) {
      return;
    }

    this.loading = true;
    this.as.register(this.form.value)
      .pipe(first())
      .subscribe({
        next: () => {
          this.als.success('Registrierung erfolgreich', {keepAfterRouteChange: true});
          this.router.navigate(['../login'], {relativeTo: this.route});
        },
        error: err => {
          this.als.error(err);
          this.loading = false;
        }
      });
  }

}
