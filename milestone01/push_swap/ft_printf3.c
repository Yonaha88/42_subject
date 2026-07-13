/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf3.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/17 11:20:24 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:27:14 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	put_per_something(const char format, int *ret)
{
	put_char('%', ret);
	if (*ret == -1)
		return ;
	put_char(format, ret);
	if (*ret == -1)
		return ;
}
