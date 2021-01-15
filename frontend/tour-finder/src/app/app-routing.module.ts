import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {HomeComponent} from './home/home.component';
import {TourListComponent} from './tour-list/tour-list.component';
import {TourDetailsComponent} from './tour-details/tour-details.component';
import {TourSearchComponent} from './tour-search/tour-search.component';
import {LayoutComponent} from './layout/layout.component';
import {LoginComponent} from './login/login.component';
import {RegisterComponent} from './register/register.component';
import {UserLayoutComponent} from './user-layout/user-layout.component';
import {UserListComponent} from './user-list/user-list.component';
import {AuthGuard} from './shared/auth.guard';


const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'home'
  },
  {
    path: 'home',
    component: HomeComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'tours',
    component: TourListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'tours/:id',
    component: TourDetailsComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'search',
    component: TourSearchComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'users',
    component: UserLayoutComponent,
    children: [
      { path: '', component: UserListComponent}
      ],
    canActivate: [AuthGuard]
  },
  {
    path: 'login',
    component: LoginComponent
  },
  {
    path: 'register',
    component: RegisterComponent
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
