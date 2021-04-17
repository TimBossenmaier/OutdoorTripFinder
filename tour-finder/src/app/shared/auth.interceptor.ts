import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import { Observable } from 'rxjs';
import {environment} from '../../environments/environment';
import {AccountService} from './account.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private accountService: AccountService) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    // add auth header if user is logged in and request is dedicated to api url
    const user = this.accountService.userValue;
    const isLoggedIn = user && user.token;
    const isApiUrl = request.url.startsWith(environment.apiUrl);

    if (request.url.startsWith(environment.apiUrl + '/auth/tokens') && isLoggedIn) {
      request = request.clone( {
        setHeaders: {
          Authorization: `Basic ${btoa(user.username + ':' + atob(user.password))}`
        }
      });
    } else {
      if (isLoggedIn && isApiUrl) {
        this.accountService.checkTokenValidity();
        console.log(user.expiration_ts, user.token);
        request = request.clone({
          setHeaders: {
            Authorization: `Basic ${btoa(user.token + ':')}`
          }
        });
      }
    }
    return next.handle(request);
  }
}
