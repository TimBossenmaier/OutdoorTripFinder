import { Injectable } from '@angular/core';
import {BehaviorSubject, Observable} from 'rxjs';
import {User} from './user';
import {Router} from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {environment} from '../../environments/environment';
import {map} from 'rxjs/operators';
import {AlertService} from './alert.service';

@Injectable({
  providedIn: 'root'
})
export class AccountService {
  private userSubject: BehaviorSubject<User>;
  public user: Observable<User>;

  constructor(
    private router: Router,
    private http: HttpClient,
    private als: AlertService
  ) {
    // get user from local browser storage if possible
    this.userSubject = new BehaviorSubject<User>(JSON.parse(localStorage.getItem('user')));
    this.user = this.userSubject.asObservable();
  }

  public get userValue(): User {
    return this.userSubject.value;
  }

  public checkTokenValidity(): void{
    const expirationDate = new Date(this.userValue.expiration_ts);
    const nowDate = new Date(Date.now());

    if (nowDate > expirationDate) {
      this.logout();
    } else {
      let diff = (expirationDate.getTime() - nowDate.getTime()) / 1000;
      diff /= 60;
      if (diff < 5) {
        this.updateToken().subscribe({
          error: err => {
            this.als.error(err);
          }
      } );
      }
    }
  }

  login(alias, password) {
    const jsonEncoded = btoa(JSON.stringify({
      output: ['id', 'username', 'email', 'password_hash', 'role_id']
    }));

    const auth = 'Basic ' + btoa(alias + ':' + password);
    return this.http.get<User>(
      `${environment.apiUrl}/auth/user/${jsonEncoded}`,
      {
        headers: {
          Authorization: auth
        }
      }
    ).pipe(
      map(user => {
        // store user details and jwt token un local storage
        user.password = btoa(password);
        localStorage.setItem('user', JSON.stringify(user));
        this.userSubject.next(user);
        return user;
      })
    );
  }

  logout() {
    localStorage.removeItem('user');
    this.userSubject.next(null);
    this.router.navigate(['/login']);
    this.als.info('Sie wurden abgemeldet', {keepAfterRouteChange: true});
  }

  register(user: User) {
    return this.http.post(`${environment.apiUrl}/auth/create_user`, user);
  }

  getAll() {
    const usersList = new BehaviorSubject<User[]>([
      new User('test', 'hallo@welt.de', 1),
      new User('testA', 'hello@world.com', 1)]);
    return usersList.asObservable();
  }

  getById(id: string){
    return new User();
  }

  update(id, params){
    return new User();
  }

  delete(id: string){
    return new User();
  }

  updateToken() {
    const jsonEncoded = btoa(JSON.stringify({
      output: ['id', 'username', 'email', 'password_hash', 'role_id']
    }));

    return this.http.get<User>(
      `${environment.apiUrl}/auth/tokens/${jsonEncoded}`
    ).pipe(
      map(user => {
        // store user details and jwt token un local storage
        localStorage.setItem('user', JSON.stringify(user));
        this.userSubject.next(user);
        return user;
      })
    );
  }

}
