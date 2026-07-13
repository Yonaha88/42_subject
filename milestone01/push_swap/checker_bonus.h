/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checker_bonus.h                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: hkanamit <hkanamit@student.42tokyo.jp>     +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:11:09 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 15:12:30 by hkanamit         ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef CHECKER_BONUS_H
# define CHECKER_BONUS_H

# include "push_swap.h"

void	pa_checker(t_list **a_lst, t_list **b_lst);
void	pb_checker(t_list **a_lst, t_list **b_lst);
void	sa_checker(t_list **a_lst);
void	sb_checker(t_list **b_lst);
void	ss_checker(t_list **a_lst, t_list **b_lst);
void	ra_checker(t_list **a_lst);
void	rb_checker(t_list **b_lst);
void	rr_checker(t_list **a_lst, t_list **b_lst);
void	rra_checker(t_list **a_lst);
void	rrb_checker(t_list **b_lst);
void	rrr_checker(t_list **a_lst, t_list **b_lst);
char	*get_line_checker(void);

#endif
